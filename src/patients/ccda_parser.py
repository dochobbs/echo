"""C-CDA XML parser for patient data extraction."""

from datetime import date, datetime
from typing import Optional, List, Tuple
from xml.etree import ElementTree as ET

from .models import (
  ImportedPatient,
  Problem,
  Medication,
  Allergy,
  Encounter,
)


# C-CDA namespaces
NS = {
  "": "urn:hl7-org:v3",
  "sdtc": "urn:hl7-org:sdtc",
  "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}


def parse_ccda(xml_content: str, source_file: Optional[str] = None) -> Tuple[ImportedPatient, List[str]]:
  """Parse C-CDA XML content into an ImportedPatient.

  Args:
    xml_content: Raw XML string content
    source_file: Optional filename for reference

  Returns:
    Tuple of (ImportedPatient, list of parse warnings)
  """
  warnings = []

  try:
    # Register namespaces
    for prefix, uri in NS.items():
      if prefix:
        ET.register_namespace(prefix, uri)
      else:
        ET.register_namespace("", uri)

    root = ET.fromstring(xml_content)
  except ET.ParseError as e:
    raise ValueError(f"Invalid XML: {e}")

  # Helper to find elements with namespace
  def find(elem, path):
    # Prepend namespace to each element in path
    ns_path = "/".join([f"{{{NS['']}}}{ p}" if p else p for p in path.split("/")])
    return elem.find(ns_path)

  def findall(elem, path):
    ns_path = "/".join([f"{{{NS['']}}}{ p}" if p else p for p in path.split("/")])
    return elem.findall(ns_path)

  # Extract patient demographics
  record_target = find(root, "recordTarget/patientRole")
  patient_elem = find(record_target, "patient") if record_target is not None else None

  name = _extract_name(patient_elem, warnings)
  birth_date = _extract_birth_date(patient_elem, warnings)
  sex = _extract_sex(patient_elem, warnings)

  # Calculate age in months if birth_date available
  age_months = None
  if birth_date:
    today = date.today()
    age_months = (today.year - birth_date.year) * 12 + (today.month - birth_date.month)

  # Extract clinical sections
  # Find structuredBody
  structured_body = find(root, "component/structuredBody")

  problems = []
  medications = []
  allergies = []
  encounters = []

  if structured_body is not None:
    for component in findall(structured_body, "component"):
      section = find(component, "section")
      if section is None:
        continue

      # Identify section by template ID or code
      template_ids = [t.get("root", "") for t in findall(section, "templateId")]
      code_elem = find(section, "code")
      section_code = code_elem.get("code", "") if code_elem is not None else ""

      # Problems (2.16.840.1.113883.10.20.22.2.5 or LOINC 11450-4)
      if "2.16.840.1.113883.10.20.22.2.5" in template_ids or section_code == "11450-4":
        problems = _extract_problems(section, warnings)

      # Medications (2.16.840.1.113883.10.20.22.2.1 or LOINC 10160-0)
      elif "2.16.840.1.113883.10.20.22.2.1" in template_ids or section_code == "10160-0":
        medications = _extract_medications(section, warnings)

      # Allergies (2.16.840.1.113883.10.20.22.2.6 or LOINC 48765-2)
      elif "2.16.840.1.113883.10.20.22.2.6" in template_ids or section_code == "48765-2":
        allergies = _extract_allergies(section, warnings)

      # Encounters (2.16.840.1.113883.10.20.22.2.22 or LOINC 46240-8)
      elif "2.16.840.1.113883.10.20.22.2.22" in template_ids or section_code == "46240-8":
        encounters = _extract_encounters(section, warnings)

  patient = ImportedPatient(
    name=name or "Unknown Patient",
    birth_date=birth_date,
    sex=sex,
    age_months=age_months,
    problems=problems,
    medications=medications,
    allergies=allergies,
    encounters=encounters,
    source="ccda",
    source_file=source_file,
  )

  return patient, warnings


def _extract_name(patient_elem, warnings: List[str]) -> Optional[str]:
  """Extract patient name from patient element."""
  if patient_elem is None:
    warnings.append("No patient element found")
    return None

  name_elem = patient_elem.find(f"{{{NS['']}}}name")
  if name_elem is None:
    warnings.append("No name element found")
    return None

  given = name_elem.find(f"{{{NS['']}}}given")
  family = name_elem.find(f"{{{NS['']}}}family")

  parts = []
  if given is not None and given.text:
    parts.append(given.text)
  if family is not None and family.text:
    parts.append(family.text)

  return " ".join(parts) if parts else None


def _extract_birth_date(patient_elem, warnings: List[str]) -> Optional[date]:
  """Extract birth date from patient element."""
  if patient_elem is None:
    return None

  birth_time = patient_elem.find(f"{{{NS['']}}}birthTime")
  if birth_time is None:
    return None

  value = birth_time.get("value", "")
  if not value:
    return None

  try:
    # C-CDA uses YYYYMMDD format
    if len(value) >= 8:
      return date(int(value[:4]), int(value[4:6]), int(value[6:8]))
  except (ValueError, IndexError):
    warnings.append(f"Could not parse birth date: {value}")

  return None


def _extract_sex(patient_elem, warnings: List[str]) -> Optional[str]:
  """Extract sex from patient element."""
  if patient_elem is None:
    return None

  admin_gender = patient_elem.find(f"{{{NS['']}}}administrativeGenderCode")
  if admin_gender is None:
    return None

  code = admin_gender.get("code", "")
  display = admin_gender.get("displayName", "")

  if code == "M" or "male" in display.lower():
    return "male"
  elif code == "F" or "female" in display.lower():
    return "female"

  return display or None


def _extract_problems(section, warnings: List[str]) -> List[Problem]:
  """Extract problems from problem section."""
  problems = []

  # Find all entries
  for entry in section.findall(f".//{{{NS['']}}}entry"):
    act = entry.find(f".//{{{NS['']}}}act")
    if act is None:
      continue

    # Get observation within act
    obs = act.find(f".//{{{NS['']}}}observation")
    if obs is None:
      continue

    # Get the code (problem)
    value_elem = obs.find(f"{{{NS['']}}}value")
    if value_elem is None:
      continue

    code = value_elem.get("code")
    code_system = value_elem.get("codeSystem")
    display = value_elem.get("displayName", "Unknown problem")

    # Map code system OID to name
    code_system_name = _map_code_system(code_system)

    # Get status
    status_code = obs.find(f".//{{{NS['']}}}statusCode")
    status = status_code.get("code", "active") if status_code is not None else "active"

    # Get onset date
    onset_date = None
    effective_time = obs.find(f"{{{NS['']}}}effectiveTime")
    if effective_time is not None:
      low = effective_time.find(f"{{{NS['']}}}low")
      if low is not None:
        value = low.get("value", "")
        if len(value) >= 8:
          try:
            onset_date = date(int(value[:4]), int(value[4:6]), int(value[6:8]))
          except (ValueError, IndexError):
            pass

    problems.append(Problem(
      code=code,
      code_system=code_system_name,
      display=display,
      onset_date=onset_date,
      status=status,
    ))

  return problems


def _extract_medications(section, warnings: List[str]) -> List[Medication]:
  """Extract medications from medication section."""
  medications = []

  for entry in section.findall(f".//{{{NS['']}}}entry"):
    subst_admin = entry.find(f".//{{{NS['']}}}substanceAdministration")
    if subst_admin is None:
      continue

    # Get the drug
    consumable = subst_admin.find(f".//{{{NS['']}}}consumable")
    if consumable is None:
      continue

    manu_product = consumable.find(f".//{{{NS['']}}}manufacturedProduct")
    if manu_product is None:
      continue

    material = manu_product.find(f".//{{{NS['']}}}manufacturedMaterial")
    if material is None:
      continue

    code_elem = material.find(f"{{{NS['']}}}code")
    if code_elem is None:
      continue

    code = code_elem.get("code")
    code_system = _map_code_system(code_elem.get("codeSystem"))
    display = code_elem.get("displayName", "Unknown medication")

    # Get dose
    dose_elem = subst_admin.find(f".//{{{NS['']}}}doseQuantity")
    dose = None
    if dose_elem is not None:
      dose_val = dose_elem.get("value", "")
      dose_unit = dose_elem.get("unit", "")
      if dose_val:
        dose = f"{dose_val} {dose_unit}".strip()

    # Get route
    route_elem = subst_admin.find(f".//{{{NS['']}}}routeCode")
    route = route_elem.get("displayName") if route_elem is not None else None

    # Get status
    status_elem = subst_admin.find(f"{{{NS['']}}}statusCode")
    status = status_elem.get("code", "active") if status_elem is not None else "active"

    medications.append(Medication(
      code=code,
      code_system=code_system,
      display=display,
      dose=dose,
      route=route,
      status=status,
    ))

  return medications


def _extract_allergies(section, warnings: List[str]) -> List[Allergy]:
  """Extract allergies from allergy section."""
  allergies = []

  for entry in section.findall(f".//{{{NS['']}}}entry"):
    act = entry.find(f".//{{{NS['']}}}act")
    if act is None:
      continue

    obs = act.find(f".//{{{NS['']}}}observation")
    if obs is None:
      continue

    # Get allergen
    participant = obs.find(f".//{{{NS['']}}}participant")
    if participant is None:
      continue

    role = participant.find(f".//{{{NS['']}}}participantRole")
    if role is None:
      continue

    entity = role.find(f".//{{{NS['']}}}playingEntity")
    if entity is None:
      continue

    code_elem = entity.find(f"{{{NS['']}}}code")
    if code_elem is None:
      continue

    code = code_elem.get("code")
    code_system = _map_code_system(code_elem.get("codeSystem"))
    display = code_elem.get("displayName", "Unknown allergen")

    # Get reaction
    reaction = None
    reaction_obs = obs.find(f".//{{{NS['']}}}entryRelationship/{{{NS['']}}}observation")
    if reaction_obs is not None:
      reaction_code = reaction_obs.find(f"{{{NS['']}}}value")
      if reaction_code is not None:
        reaction = reaction_code.get("displayName")

    # Get severity
    severity = None
    severity_obs = obs.find(f".//{{{NS['']}}}entryRelationship[@typeCode='SUBJ']/{{{NS['']}}}observation")
    if severity_obs is not None:
      severity_code = severity_obs.find(f"{{{NS['']}}}value")
      if severity_code is not None:
        severity = severity_code.get("displayName")

    allergies.append(Allergy(
      code=code,
      code_system=code_system,
      display=display,
      reaction=reaction,
      severity=severity,
    ))

  return allergies


def _extract_encounters(section, warnings: List[str]) -> List[Encounter]:
  """Extract encounters from encounters section."""
  encounters = []

  for entry in section.findall(f".//{{{NS['']}}}entry"):
    enc = entry.find(f".//{{{NS['']}}}encounter")
    if enc is None:
      continue

    # Get encounter date
    enc_date = None
    effective_time = enc.find(f"{{{NS['']}}}effectiveTime")
    if effective_time is not None:
      value = effective_time.get("value", "")
      if len(value) >= 8:
        try:
          enc_date = date(int(value[:4]), int(value[4:6]), int(value[6:8]))
        except (ValueError, IndexError):
          pass

    # Get encounter type
    code_elem = enc.find(f"{{{NS['']}}}code")
    enc_type = code_elem.get("displayName") if code_elem is not None else None

    # Get reason
    reason = None
    entry_rel = enc.find(f".//{{{NS['']}}}entryRelationship")
    if entry_rel is not None:
      obs = entry_rel.find(f".//{{{NS['']}}}observation")
      if obs is not None:
        value_elem = obs.find(f"{{{NS['']}}}value")
        if value_elem is not None:
          reason = value_elem.get("displayName")

    encounters.append(Encounter(
      date=enc_date,
      type=enc_type,
      reason=reason,
    ))

  return encounters


def _map_code_system(oid: Optional[str]) -> Optional[str]:
  """Map OID to human-readable code system name."""
  if not oid:
    return None

  oid_map = {
    "2.16.840.1.113883.6.96": "SNOMED-CT",
    "2.16.840.1.113883.6.90": "ICD-10-CM",
    "2.16.840.1.113883.6.88": "RxNorm",
    "2.16.840.1.113883.6.1": "LOINC",
    "2.16.840.1.113883.6.69": "NDC",
  }

  return oid_map.get(oid, oid)
