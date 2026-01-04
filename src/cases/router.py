"""Case management API endpoints for Echo."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from .models import (
  StartCaseRequest,
  CaseMessageRequest,
  CaseResponse,
  CaseState,
  CasePhase,
  DebriefData,
  # Describe-a-case mode
  StartDescribeCaseRequest,
  DescribeCaseMessageRequest,
  DescribeCaseResponse,
  DescribeCaseState,
  DescribeCasePhase,
  # Export & History
  CaseExportRequest,
  CaseExport,
  LearningMaterials,
  CaseHistoryResponse,
)
from .generator import get_generator
from .history import get_case_history
from .persistence import get_case_persistence, is_supabase_configured
from ..auth.deps import get_optional_user, get_current_user
from ..auth.models import User

router = APIRouter(prefix="/case", tags=["cases"])


@router.post("/start")
async def start_case(
  request: StartCaseRequest,
  user: Optional[User] = Depends(get_optional_user),
) -> CaseResponse:
  """Start a new case.

  Returns an opening message from Echo and the initial case state.
  If authenticated, the case will be persisted to the user's history.
  """
  from ..core.tutor import Tutor

  generator = get_generator()

  case_state = generator.create_case(
    condition_key=request.condition_key,
    learner_level=request.learner_level,
    time_constraint=request.time_constraint,
  )

  condition_info = generator.get_condition_info(case_state.patient.condition_key)

  tutor = Tutor()
  opening = await tutor.generate_case_opening(case_state, condition_info)

  case_state.conversation.append({
    "role": "echo",
    "content": opening,
  })

  if user and is_supabase_configured():
    persistence = get_case_persistence()
    persistence.save_session(case_state, user_id=str(user.id))

  return CaseResponse(
    message=opening,
    case_state=case_state,
  )


@router.post("/message")
async def send_message(
  request: CaseMessageRequest,
  user: Optional[User] = Depends(get_optional_user),
) -> CaseResponse:
  """Send a message in an active case.

  The tutor processes the learner's message and responds appropriately,
  tracking what has been discovered and advancing the case phase.
  Detects when the learner is stuck and offers supportive hints.
  """
  from ..core.tutor import Tutor

  case_state = request.case_state

  case_state.conversation.append({
    "role": "user",
    "content": request.message,
  })

  generator = get_generator()
  condition_info = generator.get_condition_info(case_state.patient.condition_key)

  tutor = Tutor()
  response, updated_state, teaching_moment, hint_offered = await tutor.process_case_message(
    message=request.message,
    case_state=case_state,
    condition_info=condition_info,
  )

  updated_state.conversation.append({
    "role": "echo",
    "content": response,
  })

  if user and is_supabase_configured():
    persistence = get_case_persistence()
    persistence.save_session(updated_state, user_id=str(user.id))

  return CaseResponse(
    message=response,
    case_state=updated_state,
    teaching_moment=teaching_moment,
    hint_offered=hint_offered,
  )


@router.post("/debrief")
async def get_debrief(
  case_state: CaseState,
  user: Optional[User] = Depends(get_optional_user),
) -> CaseResponse:
  """Get a debrief for a completed case.

  Summarizes what was done well, areas for improvement, and key teaching points.
  Returns structured debrief data for rich UI display.
  """
  from ..core.tutor import Tutor

  generator = get_generator()
  condition_info = generator.get_condition_info(case_state.patient.condition_key)

  tutor = Tutor()
  debrief_data = await tutor.generate_debrief(case_state, condition_info)

  case_state.phase = CasePhase.COMPLETE

  debrief = DebriefData(
    summary=debrief_data.get("summary", "Case complete."),
    strengths=debrief_data.get("strengths", []),
    areas_for_improvement=debrief_data.get("areas_for_improvement", []),
    missed_items=debrief_data.get("missed_items", []),
    teaching_points=debrief_data.get("teaching_points", []),
    follow_up_resources=debrief_data.get("follow_up_resources", []),
  )

  if user and is_supabase_configured():
    persistence = get_case_persistence()
    persistence.complete_session(
      case_state,
      debrief_summary=debrief.summary,
      user_id=str(user.id),
    )

  return CaseResponse(
    message=debrief.summary,
    case_state=case_state,
    debrief=debrief,
  )


# ==================== DESCRIBE-A-CASE MODE ====================

@router.post("/describe/start")
async def start_describe_case(request: StartDescribeCaseRequest) -> DescribeCaseResponse:
  """Start a describe-a-case session.

  The learner will describe a real case they've seen, and Echo will
  discuss it with them in a Socratic way.
  """
  from ..core.tutor import Tutor

  # Create initial state
  state = DescribeCaseState(learner_level=request.learner_level)

  # Get tutor's opening
  tutor = Tutor()
  opening = await tutor.start_describe_session(request.learner_level.value)

  # Add to conversation
  state.conversation.append({
    "role": "echo",
    "content": opening,
  })

  return DescribeCaseResponse(
    message=opening,
    state=state,
  )


@router.post("/describe/message")
async def describe_case_message(request: DescribeCaseMessageRequest) -> DescribeCaseResponse:
  """Send a message in a describe-a-case session.

  Echo will engage with the case, ask clarifying questions,
  and provide teaching when appropriate. May include citations
  from medical literature.
  """
  from ..core.tutor import Tutor

  state = request.state

  # Add learner message to conversation
  state.conversation.append({
    "role": "user",
    "content": request.message,
  })

  # Process the message
  tutor = Tutor()
  response, updated_state, citations = await tutor.process_describe_message(
    message=request.message,
    state=state,
  )

  # Add Echo's response to conversation
  updated_state.conversation.append({
    "role": "echo",
    "content": response,
  })

  return DescribeCaseResponse(
    message=response,
    state=updated_state,
    citations=citations,
  )


# ==================== CASE EXPORT & HISTORY ====================

@router.post("/export")
async def export_case(request: CaseExportRequest) -> CaseExport:
  """Export a case with learning objectives and reading list.

  Returns the full case with teaching goals, clinical pearls,
  common mistakes to avoid, red flags, and optional reading list.
  """
  case_state = request.case_state
  generator = get_generator()
  condition_info = generator.get_condition_info(case_state.patient.condition_key)

  # Build patient summary
  patient = case_state.patient
  patient_summary = {
    "name": patient.name,
    "age": patient.age,
    "age_unit": patient.age_unit,
    "sex": patient.sex,
    "weight_kg": patient.weight_kg,
    "chief_complaint": patient.chief_complaint,
    "parent_name": patient.parent_name,
    "vitals": patient.vitals,
  }

  # Build case summary
  case_summary = {
    "history_gathered": case_state.history_gathered,
    "exam_performed": case_state.exam_performed,
    "differential": case_state.differential,
    "plan_proposed": case_state.plan_proposed,
    "phase": case_state.phase.value,
    "learner_level": case_state.learner_level.value,
    "started_at": case_state.started_at.isoformat(),
    "hints_given": case_state.hints_given,
  }

  # Extract learning materials from condition YAML
  learning_materials = LearningMaterials(
    teaching_goals=condition_info.get("teaching_goals", []),
    clinical_pearls=condition_info.get("clinical_pearls", []),
    common_mistakes=condition_info.get("common_learner_mistakes", []),
    red_flags=condition_info.get("red_flags", []),
    reading_list=[],
  )

  # Generate reading list if requested
  if request.include_reading_list:
    reading_list = await _generate_reading_list(
      condition_key=patient.condition_key,
      condition_display=patient.condition_display,
    )
    learning_materials.reading_list = reading_list

  # Create the export
  export = CaseExport(
    session_id=case_state.session_id,
    condition=patient.condition_key,
    condition_display=patient.condition_display,
    patient_summary=patient_summary,
    case_summary=case_summary,
    teaching_moments=case_state.teaching_moments,
    learning_materials=learning_materials,
    conversation_transcript=case_state.conversation,
    completed_at=datetime.now(),
  )

  # Add to history
  history = get_case_history()
  history.add_completed_case(export)

  return export


@router.get("/history")
async def get_history(
  user: Optional[User] = Depends(get_optional_user),
) -> CaseHistoryResponse:
  """Get list of completed cases.

  Returns a summary list of all cases completed.
  If authenticated with Supabase, returns persisted history.
  Otherwise returns in-memory history from current session.
  """
  if user and is_supabase_configured():
    persistence = get_case_persistence()
    cases = persistence.get_user_history(str(user.id), status="completed")
    return CaseHistoryResponse(
      cases=cases,
      total_count=len(cases),
    )

  history = get_case_history()
  cases = history.get_all()

  return CaseHistoryResponse(
    cases=cases,
    total_count=history.count(),
  )


@router.get("/history/{session_id}")
async def get_case_detail(
  session_id: str,
  user: Optional[User] = Depends(get_optional_user),
) -> CaseExport:
  """Get full details of a specific completed case."""
  if user and is_supabase_configured():
    persistence = get_case_persistence()
    export = persistence.get_case_export(session_id, user_id=str(user.id))
    if export:
      return export

  history = get_case_history()
  export = history.get_by_session_id(session_id)

  if not export:
    raise HTTPException(status_code=404, detail=f"Case {session_id} not found")

  return export


@router.get("/me/active")
async def get_active_cases(
  user: User = Depends(get_current_user),
) -> CaseHistoryResponse:
  """Get active (in-progress) cases for the authenticated user."""
  if not is_supabase_configured():
    return CaseHistoryResponse(cases=[], total_count=0)

  persistence = get_case_persistence()
  cases = persistence.get_user_history(str(user.id), status="active")
  return CaseHistoryResponse(
    cases=cases,
    total_count=len(cases),
  )


async def _generate_reading_list(
  condition_key: str,
  condition_display: str,
) -> list[dict]:
  """Generate a reading list for a condition using Exa search."""
  try:
    from ..core.citations import get_citation_search

    search = get_citation_search()
    query = f"pediatric {condition_display} guidelines treatment AAP"
    result = await search.search(query, num_results=5)

    reading_list = []
    for citation in result.citations:
      reading_list.append({
        "title": citation.title,
        "url": citation.url,
        "source": citation.source,
        "snippet": citation.snippet[:200] if citation.snippet else None,
      })

    return reading_list

  except Exception:
    # Fall back to static reading list if Exa fails
    return _get_static_reading_list(condition_key)


def _get_static_reading_list(condition_key: str) -> list[dict]:
  """Get static reading list for common conditions."""
  # Maps condition keys to relevant AAP/CDC resources
  static_resources = {
    "aom": [
      {"title": "AAP Clinical Practice Guideline: AOM", "url": "https://publications.aap.org/pediatrics/article/131/3/e964/30912/", "source": "AAP"},
    ],
    "bronchiolitis": [
      {"title": "AAP Clinical Practice Guideline: Bronchiolitis", "url": "https://publications.aap.org/pediatrics/article/134/5/e1474/32997/", "source": "AAP"},
    ],
    "croup": [
      {"title": "Croup: Diagnosis and Management", "url": "https://www.aafp.org/pubs/afp/issues/2018/0901/p303.html", "source": "AAFP"},
    ],
    "pharyngitis": [
      {"title": "IDSA Guidelines for GAS Pharyngitis", "url": "https://academic.oup.com/cid/article/55/10/e86/321183", "source": "IDSA"},
    ],
    "gastroenteritis": [
      {"title": "CDC: Managing Acute Gastroenteritis", "url": "https://www.cdc.gov/mmwr/preview/mmwrhtml/rr5216a1.htm", "source": "CDC"},
    ],
    "febrile_infant": [
      {"title": "AAP Clinical Practice Guideline: Febrile Infants", "url": "https://publications.aap.org/pediatrics/article/148/2/e2021052228/179783/", "source": "AAP"},
    ],
    "uti": [
      {"title": "AAP Urinary Tract Infection Clinical Practice Guideline", "url": "https://publications.aap.org/pediatrics/article/128/3/595/30756/", "source": "AAP"},
    ],
    "asthma": [
      {"title": "NHLBI Expert Panel Report 4: Asthma Guidelines", "url": "https://www.nhlbi.nih.gov/health-topics/guidelines-for-diagnosis-management-of-asthma", "source": "NIH"},
    ],
    "atopic_dermatitis": [
      {"title": "AAP Clinical Report: Atopic Dermatitis", "url": "https://publications.aap.org/pediatrics/article/134/6/e1735/33136/", "source": "AAP"},
    ],
    "constipation": [
      {"title": "NASPGHAN Guidelines: Constipation", "url": "https://journals.lww.com/jpgn/fulltext/2014/02000/evaluation_and_treatment_of_functional.24.aspx", "source": "NASPGHAN"},
    ],
    "febrile_seizures": [
      {"title": "AAP Clinical Practice Guideline: Febrile Seizures", "url": "https://publications.aap.org/pediatrics/article/127/2/389/65091/", "source": "AAP"},
    ],
  }

  resources = static_resources.get(condition_key, [])

  # Add general pediatrics resources if we have few specific ones
  if len(resources) < 3:
    resources.append({
      "title": "UpToDate: Pediatric Topics",
      "url": "https://www.uptodate.com/",
      "source": "UpToDate",
    })
    resources.append({
      "title": "AAP Bright Futures",
      "url": "https://brightfutures.aap.org/",
      "source": "AAP",
    })

  return resources
