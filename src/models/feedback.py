"""Request and response models for Echo endpoints."""

from typing import Optional, Literal
from pydantic import BaseModel
from .context import PatientContext, EncounterContext


class FeedbackRequest(BaseModel):
  """Request feedback on a learner action."""
  patient: PatientContext
  learner_action: str
  action_type: Literal[
    "question",        # Question asked to patient
    "exam_finding",    # Physical exam performed
    "diagnosis",       # Diagnostic assessment
    "medication_order",# Medication ordered
    "lab_order",       # Lab/imaging ordered
    "referral",        # Referral placed
    "plan_item",       # Other plan element
    "documentation",   # Note written
  ]
  learner_level: Literal["student", "resident", "np_student", "fellow", "attending"] = "student"
  context: Optional[str] = None  # Additional context
  voice_response: bool = False   # Return audio?


class FeedbackResponse(BaseModel):
  """Echo's feedback response."""
  feedback: str
  feedback_type: Literal["praise", "correction", "question", "suggestion"]
  clinical_issue: Optional[str] = None  # If there's a safety/clinical concern
  follow_up_question: Optional[str] = None  # Socratic follow-up
  audio_url: Optional[str] = None  # If voice_response was True


class QuestionRequest(BaseModel):
  """Request a Socratic question about the case."""
  patient: PatientContext
  encounter: Optional[EncounterContext] = None
  learner_question: Optional[str] = None  # What the learner asked
  topic: Optional[str] = None  # Specific topic to question about
  learner_level: str = "student"
  voice_response: bool = False


class QuestionResponse(BaseModel):
  """Echo's Socratic question."""
  question: str
  hint: Optional[str] = None  # Optional gentle hint
  topic: str  # What clinical concept this addresses
  audio_url: Optional[str] = None


class DebriefRequest(BaseModel):
  """Request post-encounter debrief."""
  patient: PatientContext
  encounter: EncounterContext
  learner_level: str = "student"
  focus_areas: list[str] = []  # Specific areas to address
  voice_response: bool = False


class DebriefResponse(BaseModel):
  """Echo's debrief."""
  summary: str
  strengths: list[str]
  areas_for_improvement: list[str]
  missed_items: list[str]  # Things learner should have caught
  teaching_points: list[str]
  follow_up_resources: list[str] = []
  audio_url: Optional[str] = None
