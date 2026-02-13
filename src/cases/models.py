"""Case generation models for Echo."""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class VisitType(str, Enum):
  """Type of clinical encounter."""
  SICK = "sick"
  WELL_CHILD = "well_child"


class CasePhase(str, Enum):
  """Phases of a case encounter."""
  # Shared
  INTRO = "intro"
  EXAM = "exam"
  DEBRIEF = "debrief"
  COMPLETE = "complete"
  # Sick visit
  HISTORY = "history"
  ASSESSMENT = "assessment"
  PLAN = "plan"
  # Well-child
  GROWTH_REVIEW = "growth_review"
  DEVELOPMENTAL_SCREENING = "developmental_screening"
  ANTICIPATORY_GUIDANCE = "anticipatory_guidance"
  IMMUNIZATIONS = "immunizations"
  PARENT_QUESTIONS = "parent_questions"


class CaseImage(BaseModel):
  """An image associated with a case for teaching purposes."""
  key: str  # e.g., "target_lesion", "slapped_cheek"
  url: str  # Public URL to the image
  caption: str  # Description shown with the image
  phase: str  # When to show: intro, history, exam, assessment, debrief
  alt_text: Optional[str] = None  # Accessibility text
  source: Optional[str] = None  # Attribution, e.g., "CDC PHIL #4508"


class LearnerLevel(str, Enum):
  """Learner experience levels."""
  STUDENT = "student"
  RESIDENT = "resident"
  NP_STUDENT = "np_student"
  FELLOW = "fellow"
  ATTENDING = "attending"


class GeneratedPatient(BaseModel):
  """A generated patient for a case."""
  id: str = Field(default_factory=lambda: str(uuid.uuid4()))
  name: str
  age: int
  age_unit: str = "months"  # days, weeks, months, years
  sex: str  # male, female
  weight_kg: float
  chief_complaint: Optional[str] = None
  parent_name: str
  parent_style: str  # anxious, experienced, hesitant, rushed
  condition_key: str

  # Hidden from learner until discovered
  condition_display: str  # e.g., "Acute Otitis Media"
  symptoms: list[str]
  vitals: dict[str, float]
  exam_findings: list[dict]

  # Well-child specific
  visit_age_months: Optional[int] = None
  growth_data: Optional[dict] = None
  milestones: Optional[dict] = None
  immunization_history: Optional[list] = None
  incidental_finding: Optional[dict] = None


class CaseState(BaseModel):
  """State of an active case."""
  session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
  phase: CasePhase = CasePhase.INTRO
  patient: GeneratedPatient
  learner_level: LearnerLevel = LearnerLevel.STUDENT
  visit_type: VisitType = VisitType.SICK

  # Sick visit tracking
  history_gathered: list[str] = Field(default_factory=list)
  exam_performed: list[str] = Field(default_factory=list)
  differential: list[str] = Field(default_factory=list)
  plan_proposed: list[str] = Field(default_factory=list)

  # Well-child tracking
  growth_reviewed: bool = False
  milestones_assessed: list[str] = Field(default_factory=list)
  guidance_topics_covered: list[str] = Field(default_factory=list)
  immunizations_addressed: bool = False
  screening_tools_used: list[str] = Field(default_factory=list)
  parent_concerns_addressed: list[str] = Field(default_factory=list)

  # Teaching tracking
  hints_given: int = 0
  teaching_moments: list[str] = Field(default_factory=list)

  # Timing
  started_at: datetime = Field(default_factory=datetime.now)
  time_constraint: Optional[int] = None  # minutes, if set

  # Conversation history for context
  conversation: list[dict] = Field(default_factory=list)


class CaseSeverity(str, Enum):
  """Severity levels for case variants."""
  MILD = "mild"
  MODERATE = "moderate"
  SEVERE = "severe"


class AgeBracket(str, Enum):
  """Age brackets for case variants."""
  NEONATE = "neonate"      # 0-28 days
  INFANT = "infant"        # 1-12 months
  TODDLER = "toddler"      # 1-3 years
  CHILD = "child"          # 3-12 years
  ADOLESCENT = "adolescent"  # 12-18 years


class CasePresentation(str, Enum):
  """Presentation types for case variants."""
  TYPICAL = "typical"
  ATYPICAL = "atypical"
  EARLY = "early"
  LATE = "late"


class CaseComplexity(str, Enum):
  """Complexity levels for case variants."""
  STRAIGHTFORWARD = "straightforward"
  NUANCED = "nuanced"
  CHALLENGING = "challenging"


class StartCaseRequest(BaseModel):
  """Request to start a new case."""
  learner_level: LearnerLevel = LearnerLevel.STUDENT
  condition_key: Optional[str] = None  # Optional: request specific condition
  time_constraint: Optional[int] = None  # Minutes available
  visit_type: VisitType = VisitType.SICK
  visit_age_months: Optional[int] = None  # Required for well-child cases

  # Variant controls - None means Claude picks randomly
  severity: Optional[CaseSeverity] = None
  age_bracket: Optional[AgeBracket] = None
  presentation: Optional[CasePresentation] = None
  complexity: Optional[CaseComplexity] = None


class CaseMessageRequest(BaseModel):
  """Request to send a message in a case."""
  message: str
  case_state: CaseState


class DomainScore(BaseModel):
  """Score for a single well-child domain."""
  score: int = Field(ge=0, le=10)
  feedback: str


class WellChildScores(BaseModel):
  """Domain scores for well-child case debrief."""
  growth_interpretation: DomainScore
  milestone_assessment: DomainScore
  exam_thoroughness: DomainScore
  anticipatory_guidance: DomainScore
  immunization_knowledge: DomainScore
  communication_skill: DomainScore


class DebriefData(BaseModel):
  """Structured debrief data for case completion."""
  summary: str
  strengths: list[str] = Field(default_factory=list)
  areas_for_improvement: list[str] = Field(default_factory=list)
  missed_items: list[str] = Field(default_factory=list)
  teaching_points: list[str] = Field(default_factory=list)
  follow_up_resources: list[str] = Field(default_factory=list)
  well_child_scores: Optional[WellChildScores] = None


class CaseResponse(BaseModel):
  """Response from Echo in a case."""
  message: str
  case_state: CaseState
  teaching_moment: Optional[str] = None
  debrief: Optional[DebriefData] = None  # Present when phase is complete
  hint_offered: bool = False  # True if Echo offered help due to detected struggle
  images: list[CaseImage] = Field(default_factory=list)  # Images relevant to current phase


# ==================== DESCRIBE-A-CASE MODE ====================

class DescribeCasePhase(str, Enum):
  """Phases of a described case discussion."""
  LISTENING = "listening"        # Echo is gathering the case details
  DISCUSSING = "discussing"      # Active discussion of the case
  TEACHING = "teaching"          # Focused teaching based on the case
  COMPLETE = "complete"


class DescribedCase(BaseModel):
  """A case described by the learner."""
  id: str = Field(default_factory=lambda: str(uuid.uuid4()))
  # These are filled in as the learner shares
  chief_complaint: Optional[str] = None
  age_description: Optional[str] = None  # "3 year old", "infant", etc
  key_history: list[str] = Field(default_factory=list)
  key_findings: list[str] = Field(default_factory=list)
  learner_assessment: Optional[str] = None
  learner_plan: Optional[str] = None
  actual_outcome: Optional[str] = None  # What actually happened


class DescribeCaseState(BaseModel):
  """State of a describe-a-case session."""
  session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
  phase: DescribeCasePhase = DescribeCasePhase.LISTENING
  learner_level: LearnerLevel = LearnerLevel.STUDENT
  case: DescribedCase = Field(default_factory=DescribedCase)

  # What we've discussed
  topics_covered: list[str] = Field(default_factory=list)
  teaching_points: list[str] = Field(default_factory=list)
  citations: list[dict] = Field(default_factory=list)  # Exa citations

  # Conversation history
  conversation: list[dict] = Field(default_factory=list)

  # Timing
  started_at: datetime = Field(default_factory=datetime.now)


class StartDescribeCaseRequest(BaseModel):
  """Request to start a describe-a-case session."""
  learner_level: LearnerLevel = LearnerLevel.STUDENT


class DescribeCaseMessageRequest(BaseModel):
  """Message in a describe-a-case session."""
  message: str
  state: DescribeCaseState


class DescribeCaseResponse(BaseModel):
  """Response from Echo in describe-a-case mode."""
  message: str
  state: DescribeCaseState
  citations: Optional[list[dict]] = None  # Relevant citations if any


# ==================== CASE EXPORT & HISTORY ====================

class CaseExportRequest(BaseModel):
  """Request to export a case with learning materials."""
  case_state: CaseState
  include_reading_list: bool = True


class LearningMaterials(BaseModel):
  """Learning materials for a completed case."""
  teaching_goals: list[str] = Field(default_factory=list)
  clinical_pearls: list[str] = Field(default_factory=list)
  common_mistakes: list[str] = Field(default_factory=list)
  red_flags: list[str] = Field(default_factory=list)
  reading_list: list[dict] = Field(default_factory=list)  # [{title, url, source}]


class CaseExport(BaseModel):
  """Exported case with learning materials."""
  session_id: str
  condition: str
  condition_display: str
  patient_summary: dict
  case_summary: dict  # history, exam, differential, plan
  teaching_moments: list[str]
  learning_materials: LearningMaterials
  conversation_transcript: list[dict]
  completed_at: datetime = Field(default_factory=datetime.now)


class CompletedCaseSummary(BaseModel):
  """Summary of a completed case for history list."""
  session_id: str
  condition_display: str
  patient_name: str
  patient_age: str
  learner_level: str
  completed_at: datetime
  duration_minutes: Optional[int] = None
  teaching_moments_count: int = 0


class CaseHistoryResponse(BaseModel):
  """List of completed cases."""
  cases: list[CompletedCaseSummary]
  total_count: int


# ==================== POST-DEBRIEF Q&A ====================

class DebriefDetail(BaseModel):
  """Full debrief details for a completed case."""
  session_id: str
  condition_display: str
  patient_name: str
  patient_age: str
  summary: str
  strengths: list[str] = Field(default_factory=list)
  areas_for_improvement: list[str] = Field(default_factory=list)
  missed_items: list[str] = Field(default_factory=list)
  teaching_points: list[str] = Field(default_factory=list)
  follow_up_resources: list[str] = Field(default_factory=list)
  completed_at: Optional[datetime] = None


class PostDebriefQuestionRequest(BaseModel):
  """Request to ask a follow-up question about a completed case."""
  question: str
  # Optional: include previous Q&A context for multi-turn conversation
  previous_questions: list[dict] = Field(default_factory=list)  # [{question, answer}]


class PostDebriefQuestionResponse(BaseModel):
  """Response to a post-debrief question."""
  answer: str
  related_teaching_points: list[str] = Field(default_factory=list)
  citations: Optional[list[dict]] = None
