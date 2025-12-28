"""Context models shared across platforms."""

from typing import Optional, Literal
from pydantic import BaseModel
from datetime import date


class Condition(BaseModel):
  """Problem list entry."""
  display_name: str
  code: Optional[str] = None
  code_system: Optional[str] = None
  is_active: bool = True
  onset_date: Optional[date] = None


class Medication(BaseModel):
  """Medication entry."""
  display_name: str
  dose: Optional[str] = None
  frequency: Optional[str] = None
  code: Optional[str] = None
  is_active: bool = True


class Allergy(BaseModel):
  """Allergy entry."""
  display_name: str
  reaction: Optional[str] = None
  severity: Optional[str] = None


class EncounterSummary(BaseModel):
  """Brief encounter summary."""
  date: date
  type: str
  chief_complaint: str
  diagnoses: list[str] = []
  provider: Optional[str] = None


class PatientContext(BaseModel):
  """
  Shared patient context from any platform.
  This is the common format Oread, Syrinx, and Mneme all send to Echo.
  """
  patient_id: str
  source: Literal["oread", "syrinx", "mneme"]

  # Demographics
  name: str
  age_years: Optional[int] = None
  age_months: Optional[int] = None
  sex: Optional[str] = None

  # Clinical data
  problem_list: list[Condition] = []
  medication_list: list[Medication] = []
  allergy_list: list[Allergy] = []
  recent_encounters: list[EncounterSummary] = []

  # Optional extended context
  family_history: Optional[str] = None
  social_history: Optional[str] = None

  @property
  def age_display(self) -> str:
    """Human-readable age."""
    if self.age_years and self.age_years >= 2:
      return f"{self.age_years} years"
    elif self.age_months:
      return f"{self.age_months} months"
    elif self.age_years:
      return f"{self.age_years * 12} months"
    return "unknown age"


class EncounterContext(BaseModel):
  """
  Context for an active encounter (used with Syrinx).
  """
  patient: PatientContext
  encounter_type: str  # "acute", "well-child", "follow-up", "mental-health"
  chief_complaint: str
  phase: str  # "history", "exam", "assessment", "plan"

  # What's happened so far
  history_gathered: list[str] = []
  exam_findings: list[str] = []
  differential: list[str] = []
  orders_placed: list[str] = []

  # Errors detected (for Syrinx error injection scenarios)
  known_errors: list[str] = []
