"""Patient import router for Echo."""

from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status
from pydantic import BaseModel

from ..auth.deps import get_current_user, get_optional_user
from ..auth.models import User
from ..database import get_db, is_database_configured

from .models import (
  ImportedPatient,
  PatientListResponse,
  PatientImportResponse,
  BulkImportResponse,
  BulkImportResult,
)
from .ccda_parser import parse_ccda


router = APIRouter(prefix="/patients", tags=["patients"])


# In-memory storage for patients when DB not configured
_memory_patients: dict[str, List[ImportedPatient]] = {}


def _get_user_patients(user_id: str) -> List[ImportedPatient]:
  """Get in-memory patients for a user."""
  if user_id not in _memory_patients:
    _memory_patients[user_id] = []
  return _memory_patients[user_id]


@router.post("/import", response_model=PatientImportResponse)
async def import_patient(
  file: UploadFile = File(...),
  user: User = Depends(get_current_user),
):
  """Import a patient from a C-CDA XML file.

  Parses the C-CDA document and extracts:
  - Demographics (name, DOB, sex)
  - Problem list
  - Medication list
  - Allergy list
  - Recent encounters
  """
  # Validate file type
  if not file.filename:
    raise HTTPException(status_code=400, detail="No filename provided")

  if not file.filename.endswith((".xml", ".cda", ".ccda")):
    raise HTTPException(
      status_code=400,
      detail="File must be XML format (.xml, .cda, or .ccda)",
    )

  # Read file content
  try:
    content = await file.read()
    xml_content = content.decode("utf-8")
  except UnicodeDecodeError:
    raise HTTPException(status_code=400, detail="File must be valid UTF-8 encoded XML")

  # Parse C-CDA
  try:
    patient, warnings = parse_ccda(xml_content, source_file=file.filename)
  except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))

  # Set user ID
  patient.user_id = str(user.id)

  # Store patient
  # For now, use in-memory storage
  # TODO: Add database persistence
  patients = _get_user_patients(str(user.id))
  patients.append(patient)

  return PatientImportResponse(
    patient=patient,
    parse_warnings=warnings,
  )


@router.post("/import/bulk", response_model=BulkImportResponse)
async def bulk_import_patients(
  files: List[UploadFile] = File(...),
  user: User = Depends(get_current_user),
):
  """Import multiple patients from C-CDA XML files.

  Accepts up to 50 files at once. Returns results for each file.
  """
  if len(files) > 50:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Maximum 50 files allowed per upload",
    )

  results: List[BulkImportResult] = []
  patients = _get_user_patients(str(user.id))

  for file in files:
    filename = file.filename or "unknown"
    
    if not filename.endswith((".xml", ".cda", ".ccda")):
      results.append(BulkImportResult(
        filename=filename,
        success=False,
        error="File must be XML format (.xml, .cda, or .ccda)",
      ))
      continue

    try:
      content = await file.read()
      xml_content = content.decode("utf-8")
    except UnicodeDecodeError:
      results.append(BulkImportResult(
        filename=filename,
        success=False,
        error="File must be valid UTF-8 encoded XML",
      ))
      continue

    try:
      patient, warnings = parse_ccda(xml_content, source_file=filename)
      patient.user_id = str(user.id)
      patients.append(patient)
      
      results.append(BulkImportResult(
        filename=filename,
        success=True,
        patient=patient,
        warnings=warnings,
      ))
    except ValueError as e:
      results.append(BulkImportResult(
        filename=filename,
        success=False,
        error=str(e),
      ))

  successful = sum(1 for r in results if r.success)
  
  return BulkImportResponse(
    results=results,
    total_files=len(files),
    successful=successful,
    failed=len(files) - successful,
  )


@router.get("", response_model=PatientListResponse)
async def list_patients(
  user: User = Depends(get_current_user),
):
  """List all imported patients for the current user."""
  patients = _get_user_patients(str(user.id))

  return PatientListResponse(
    patients=patients,
    total_count=len(patients),
  )


@router.get("/{patient_id}", response_model=ImportedPatient)
async def get_patient(
  patient_id: str,
  user: User = Depends(get_current_user),
):
  """Get a specific imported patient."""
  patients = _get_user_patients(str(user.id))

  for patient in patients:
    if patient.id == patient_id:
      return patient

  raise HTTPException(status_code=404, detail="Patient not found")


@router.delete("/{patient_id}")
async def delete_patient(
  patient_id: str,
  user: User = Depends(get_current_user),
):
  """Delete an imported patient from the user's panel."""
  patients = _get_user_patients(str(user.id))

  for i, patient in enumerate(patients):
    if patient.id == patient_id:
      patients.pop(i)
      return {"message": "Patient deleted", "patient_id": patient_id}

  raise HTTPException(status_code=404, detail="Patient not found")


class PatientContextForCase(BaseModel):
  """Patient context to use when starting a case."""
  patient_id: str
  include_problems: bool = True
  include_medications: bool = True
  include_allergies: bool = True


def get_patient_context_for_case(
  patient_id: str,
  user_id: str,
) -> Optional[dict]:
  """Get patient context suitable for case generation.

  Returns dict with patient data that can be incorporated into
  the case generation prompt.
  """
  patients = _get_user_patients(user_id)

  for patient in patients:
    if patient.id == patient_id:
      return {
        "name": patient.name,
        "age_months": patient.age_months,
        "sex": patient.sex,
        "problems": [
          {"display": p.display, "code": p.code, "status": p.status}
          for p in patient.problems if p.status == "active"
        ],
        "medications": [
          {"display": m.display, "dose": m.dose}
          for m in patient.medications if m.status == "active"
        ],
        "allergies": [
          {"display": a.display, "reaction": a.reaction, "severity": a.severity}
          for a in patient.allergies
        ],
        "recent_encounters": [
          {"date": str(e.date) if e.date else None, "type": e.type, "reason": e.reason}
          for e in patient.encounters[:5]  # Last 5 encounters
        ],
      }

  return None
