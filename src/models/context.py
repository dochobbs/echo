"""Context models shared across platforms."""

from typing import Optional, Literal, Union
from pydantic import BaseModel, model_validator
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


class WidgetPatientContext(BaseModel):
  """
  Simplified patient context for widget consumers.
  Uses camelCase and simple string arrays for easier JavaScript integration.
  """
  patientId: str
  source: Literal["oread", "syrinx", "mneme"] = "oread"

  # Demographics (simplified)
  name: Optional[str] = None
  age: Optional[int] = None  # Will be treated as years
  sex: Optional[str] = None
  chiefComplaint: Optional[str] = None

  # Simple string lists (will be converted to complex types)
  problemList: Optional[list[str]] = None
  medications: Optional[list[str]] = None
  allergies: Optional[list[str]] = None

  def to_patient_context(self) -> PatientContext:
    """Convert to full PatientContext for backend processing."""
    return PatientContext(
      patient_id=self.patientId,
      source=self.source,
      name=self.name or "Unknown",
      age_years=self.age,
      sex=self.sex,
      problem_list=[Condition(display_name=p) for p in (self.problemList or [])],
      medication_list=[Medication(display_name=m) for m in (self.medications or [])],
      allergy_list=[Allergy(display_name=a) for a in (self.allergies or [])],
    )


# Type alias for accepting either format
FlexiblePatientContext = Union[PatientContext, WidgetPatientContext]


def normalize_patient_context(patient: Optional[FlexiblePatientContext]) -> Optional[PatientContext]:
  """Convert any patient context format to the standard PatientContext."""
  if patient is None:
    return None
  if isinstance(patient, WidgetPatientContext):
    return patient.to_patient_context()
  return patient
