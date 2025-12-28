"""Core tutor logic using Claude."""

from functools import lru_cache
import anthropic

from ..config import get_settings
from ..models import PatientContext
from ..models.feedback import (
  FeedbackRequest, FeedbackResponse,
  QuestionRequest, QuestionResponse,
  DebriefRequest, DebriefResponse,
)


SYSTEM_PROMPT = """You are Echo, an AI attending physician and medical educator. You work with medical learners (students, residents, NP students) to help them develop clinical reasoning skills.

Your teaching philosophy:
1. SOCRATIC METHOD: Ask questions rather than giving answers. Guide learners to discover insights themselves.
2. PATIENT SAFETY FIRST: If there's a safety issue (allergy, contraindication, missed red flag), address it clearly.
3. SPECIFIC FEEDBACK: Reference actual patient data, not generic advice.
4. APPROPRIATE LEVEL: Adjust complexity to learner level (student vs resident vs fellow).
5. ENCOURAGING: Build confidence while correcting errors. Never belittle.
6. CLINICAL ACCURACY: Your medical knowledge must be correct.

When reviewing actions:
- Praise good clinical reasoning, not just correct answers
- When correcting, explain the "why"
- Ask follow-up questions to deepen understanding
- Connect to broader clinical principles

Tone: Warm, supportive, intellectually curious. Like the best attending you ever had."""


def format_patient_context(patient: PatientContext) -> str:
  """Format patient context for the prompt."""
  lines = [
    f"PATIENT: {patient.name}, {patient.age_display}, {patient.sex or 'sex unknown'}",
    f"Source: {patient.source}",
  ]

  if patient.problem_list:
    active = [c.display_name for c in patient.problem_list if c.is_active]
    if active:
      lines.append(f"Active Problems: {', '.join(active)}")

  if patient.medication_list:
    meds = [m.display_name for m in patient.medication_list if m.is_active]
    if meds:
      lines.append(f"Medications: {', '.join(meds)}")

  if patient.allergy_list:
    allergies = [f"{a.display_name} ({a.reaction})" if a.reaction else a.display_name
                 for a in patient.allergy_list]
    lines.append(f"ALLERGIES: {', '.join(allergies)}")

  if patient.recent_encounters:
    enc = patient.recent_encounters[0]
    lines.append(f"Last visit: {enc.date} - {enc.chief_complaint}")

  return "\n".join(lines)


class Tutor:
  """Claude-powered medical tutor."""

  def __init__(self, api_key: str, model: str):
    self.client = anthropic.Anthropic(api_key=api_key)
    self.model = model

  async def provide_feedback(self, request: FeedbackRequest) -> FeedbackResponse:
    """Provide feedback on a learner action."""
    patient_context = format_patient_context(request.patient)

    prompt = f"""{patient_context}

LEARNER LEVEL: {request.learner_level}
ACTION TYPE: {request.action_type}
LEARNER ACTION: {request.learner_action}
{f"ADDITIONAL CONTEXT: {request.context}" if request.context else ""}

Provide feedback on this action. Consider:
1. Is this clinically appropriate for this patient?
2. Are there safety concerns (allergies, contraindications)?
3. What's the clinical reasoning behind this choice?
4. What follow-up question would help the learner think deeper?

Respond in JSON format:
{{"feedback": "your feedback", "feedback_type": "praise|correction|question|suggestion", "clinical_issue": "if any safety concern, describe it, else null", "follow_up_question": "a Socratic question to deepen understanding"}}"""

    response = self.client.messages.create(
      model=self.model,
      max_tokens=1024,
      system=SYSTEM_PROMPT,
      messages=[{"role": "user", "content": prompt}]
    )

    # Parse response (in production, add proper JSON parsing)
    content = response.content[0].text
    import json
    try:
      data = json.loads(content)
      return FeedbackResponse(**data)
    except json.JSONDecodeError:
      # Fallback if Claude doesn't return valid JSON
      return FeedbackResponse(
        feedback=content,
        feedback_type="suggestion",
      )

  async def ask_socratic_question(self, request: QuestionRequest) -> QuestionResponse:
    """Generate a Socratic question."""
    patient_context = format_patient_context(request.patient)

    prompt = f"""{patient_context}

LEARNER LEVEL: {request.learner_level}
{f"LEARNER ASKED: {request.learner_question}" if request.learner_question else ""}
{f"FOCUS TOPIC: {request.topic}" if request.topic else ""}

Generate a Socratic question to help this learner think through the case. Don't give the answer - ask a question that guides them to discover it.

Respond in JSON format:
{{"question": "your Socratic question", "hint": "optional gentle hint or null", "topic": "clinical concept this addresses"}}"""

    response = self.client.messages.create(
      model=self.model,
      max_tokens=512,
      system=SYSTEM_PROMPT,
      messages=[{"role": "user", "content": prompt}]
    )

    content = response.content[0].text
    import json
    try:
      data = json.loads(content)
      return QuestionResponse(**data)
    except json.JSONDecodeError:
      return QuestionResponse(
        question=content,
        topic="clinical reasoning",
      )

  async def debrief_encounter(self, request: DebriefRequest) -> DebriefResponse:
    """Provide post-encounter debrief."""
    patient_context = format_patient_context(request.patient)
    enc = request.encounter

    prompt = f"""{patient_context}

ENCOUNTER TYPE: {enc.encounter_type}
CHIEF COMPLAINT: {enc.chief_complaint}

HISTORY GATHERED: {', '.join(enc.history_gathered) if enc.history_gathered else 'none documented'}
EXAM FINDINGS: {', '.join(enc.exam_findings) if enc.exam_findings else 'none documented'}
DIFFERENTIAL: {', '.join(enc.differential) if enc.differential else 'none documented'}
ORDERS: {', '.join(enc.orders_placed) if enc.orders_placed else 'none'}

{f"KNOWN ERRORS IN SCENARIO: {', '.join(enc.known_errors)}" if enc.known_errors else ""}

LEARNER LEVEL: {request.learner_level}
{f"FOCUS AREAS: {', '.join(request.focus_areas)}" if request.focus_areas else ""}

Provide a comprehensive debrief of this encounter. Be specific about what went well and what could improve.

Respond in JSON format:
{{
  "summary": "2-3 sentence overall summary",
  "strengths": ["list of things done well"],
  "areas_for_improvement": ["specific improvement areas"],
  "missed_items": ["things the learner should have caught"],
  "teaching_points": ["key clinical pearls from this case"],
  "follow_up_resources": ["optional reading/resources"]
}}"""

    response = self.client.messages.create(
      model=self.model,
      max_tokens=2048,
      system=SYSTEM_PROMPT,
      messages=[{"role": "user", "content": prompt}]
    )

    content = response.content[0].text
    import json
    try:
      data = json.loads(content)
      return DebriefResponse(**data)
    except json.JSONDecodeError:
      return DebriefResponse(
        summary=content,
        strengths=[],
        areas_for_improvement=[],
        missed_items=[],
        teaching_points=[],
      )


@lru_cache
def get_tutor() -> Tutor:
  """Get cached tutor instance."""
  settings = get_settings()
  return Tutor(
    api_key=settings.anthropic_api_key,
    model=settings.claude_model,
  )
