"""Models for imported patients."""

from datetime import datetime, date
from typing import Optional, List
from uuid import UUID
import uuid

from pydantic import BaseModel, Field


class Problem(BaseModel):
  """A problem/condition from the patient's problem list."""
  code: Optional[str] = None  # SNOMED or ICD-10
  code_system: Optional[str] = None
  display: str
  onset_date: Optional[date] = None
  status: str = "active"


class Medication(BaseModel):
  """A medication from the patient's medication list."""
  code: Optional[str] = None  # RxNorm
  code_system: Optional[str] = None
  display: str
  dose: Optional[str] = None
  route: Optional[str] = None
  frequency: Optional[str] = None
  status: str = "active"


class Allergy(BaseModel):
  """An allergy from the patient's allergy list."""
  code: Optional[str] = None
  code_system: Optional[str] = None
  display: str
  reaction: Optional[str] = None
  severity: Optional[str] = None


class Encounter(BaseModel):
  """A past encounter from the patient's history."""
  date: Optional[date] = None
  type: Optional[str] = None
  reason: Optional[str] = None
  provider: Optional[str] = None


class ImportedPatient(BaseModel):
  """A patient imported from C-CDA or other source."""
  id: str = Field(default_factory=lambda: str(uuid.uuid4()))
  user_id: Optional[str] = None

  # Demographics
  name: str
  birth_date: Optional[date] = None
  sex: Optional[str] = None
  age_months: Optional[int] = None  # Calculated from birth_date

  # Clinical data
  problems: List[Problem] = Field(default_factory=list)
  medications: List[Medication] = Field(default_factory=list)
  allergies: List[Allergy] = Field(default_factory=list)
  encounters: List[Encounter] = Field(default_factory=list)

  # Metadata
  source: str = "ccda"  # ccda, oread, manual
  source_file: Optional[str] = None
  imported_at: datetime = Field(default_factory=datetime.utcnow)


class PatientListResponse(BaseModel):
  """Response for listing imported patients."""
  patients: List[ImportedPatient]
  total_count: int


class PatientImportResponse(BaseModel):
  """Response after importing a patient."""
  patient: ImportedPatient
  parse_warnings: List[str] = Field(default_factory=list)
