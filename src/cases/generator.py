"""Case generator for Echo - creates patients from condition definitions."""

import random
from pathlib import Path
from typing import Optional
import yaml

from .models import GeneratedPatient, CaseState, LearnerLevel

# Load conditions from YAML
KNOWLEDGE_DIR = Path(__file__).parent.parent.parent / "knowledge" / "conditions"

# First names for generated patients
FIRST_NAMES = {
  "male": ["Liam", "Noah", "Oliver", "James", "Lucas", "Mason", "Ethan", "Aiden", "Leo", "Jack"],
  "female": ["Emma", "Olivia", "Ava", "Sophia", "Isabella", "Mia", "Luna", "Harper", "Evelyn", "Aria"],
}

# Parent names
PARENT_NAMES = [
  "Sarah", "Jennifer", "Jessica", "Ashley", "Amanda",
  "Michael", "David", "Chris", "Brian", "Jason",
]

# Last names
LAST_NAMES = [
  "Smith", "Johnson", "Williams", "Brown", "Jones",
  "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
]


class CaseGenerator:
  """Generates cases from condition definitions."""

  def __init__(self):
    self.conditions: dict = {}
    self._load_conditions()

  def _load_conditions(self):
    """Load all condition YAML files."""
    if not KNOWLEDGE_DIR.exists():
      return

    for yaml_file in KNOWLEDGE_DIR.glob("*.yaml"):
      with open(yaml_file) as f:
        data = yaml.safe_load(f)
        if data:
          # Check if this is a single-condition file (has display_name at top level)
          # or a multi-condition file (has condition keys at top level)
          if "display_name" in data:
            # Single condition file - use filename as key
            condition_key = yaml_file.stem  # e.g., "croup" from "croup.yaml"
            self.conditions[condition_key] = data
          else:
            # Multi-condition file or file with condition keys at top level
            self.conditions.update(data)

  def generate_patient(
    self,
    condition_key: Optional[str] = None,
    learner_level: LearnerLevel = LearnerLevel.STUDENT,
  ) -> GeneratedPatient:
    """Generate a patient for a case."""

    # Select condition - random if not specified
    if condition_key is None:
      available_conditions = list(self.conditions.keys())
      if not available_conditions:
        raise ValueError("No conditions available")
      condition_key = random.choice(available_conditions)

    condition = self.conditions.get(condition_key)
    if not condition:
      raise ValueError(f"Unknown condition: {condition_key}")

    # Generate demographics
    demographics = condition.get("demographics", {})
    age_info = demographics.get("age_months", {"min": 6, "max": 36})

    # Pick age from peak range if available
    peak = age_info.get("peak", [age_info.get("min", 6), age_info.get("max", 36)])
    age_months = random.randint(peak[0], peak[1])

    # Convert to appropriate unit
    if age_months < 1:
      age = max(1, age_months * 4)  # weeks
      age_unit = "weeks"
    elif age_months < 24:
      age = age_months
      age_unit = "months"
    else:
      age = age_months // 12
      age_unit = "years"

    # Gender
    gender_bias = demographics.get("gender_bias", {"male": 0.5, "female": 0.5})
    sex = "male" if random.random() < gender_bias.get("male", 0.5) else "female"

    # Generate weight based on age (rough approximation)
    if age_months < 12:
      weight_kg = 3.5 + (age_months * 0.5)  # ~0.5kg/month in first year
    else:
      weight_kg = 9 + ((age_months - 12) * 0.2)  # ~0.2kg/month after

    # Pick names
    first_name = random.choice(FIRST_NAMES[sex])
    last_name = random.choice(LAST_NAMES)
    parent_name = random.choice(PARENT_NAMES)

    # Select parent style
    parent_styles = condition.get("parent_styles", [{"key": "anxious"}])
    parent_style_info = random.choice(parent_styles)
    parent_style = parent_style_info.get("key", "anxious")

    # Generate chief complaint
    chief_complaints = condition.get("presentation", {}).get("chief_complaints", [])
    if chief_complaints:
      chief_complaint = random.choice(chief_complaints)
    else:
      chief_complaint = f"My child has {condition.get('display_name', 'symptoms')}"

    # Generate symptoms (based on probabilities)
    symptoms_config = condition.get("presentation", {}).get("symptoms", [])
    symptoms = []
    for symptom in symptoms_config:
      if isinstance(symptom, str):
        # Simple string format - include all symptoms
        symptoms.append(symptom)
      elif isinstance(symptom, dict):
        # Dict format with probability - sample based on probability
        if random.random() < symptom.get("probability", 0.5):
          symptoms.append(symptom.get("name", ""))

    # Generate vitals
    vitals_impact = condition.get("vitals_impact", {})
    temp_range = vitals_impact.get("temp_f", [98.6, 98.6])
    temp = random.uniform(temp_range[0], temp_range[1])

    # Base vitals by age, then apply multipliers
    base_hr = 120 if age_months < 12 else (110 if age_months < 36 else 100)
    base_rr = 30 if age_months < 12 else (24 if age_months < 36 else 20)

    vitals = {
      "temp_f": round(temp, 1),
      "heart_rate": int(base_hr * vitals_impact.get("hr_multiplier", 1.0)),
      "respiratory_rate": int(base_rr * vitals_impact.get("rr_multiplier", 1.0)),
      "spo2": vitals_impact.get("spo2_min", 98),
    }

    # Generate exam findings (based on probabilities)
    exam_config = condition.get("presentation", {}).get("physical_exam", [])
    exam_findings = []
    for finding in exam_config:
      if isinstance(finding, dict):
        # Check probability if present, otherwise include all
        if random.random() < finding.get("probability", 0.8):
          exam_findings.append({
            "system": finding.get("system", "general"),
            "finding": finding.get("finding", ""),
          })

    return GeneratedPatient(
      name=f"{first_name} {last_name}",
      age=age,
      age_unit=age_unit,
      sex=sex,
      weight_kg=round(weight_kg, 1),
      chief_complaint=chief_complaint,
      parent_name=parent_name,
      parent_style=parent_style,
      condition_key=condition_key,
      condition_display=condition.get("display_name", condition_key),
      symptoms=symptoms,
      vitals=vitals,
      exam_findings=exam_findings,
    )

  def create_case(
    self,
    condition_key: Optional[str] = None,
    learner_level: LearnerLevel = LearnerLevel.STUDENT,
    time_constraint: Optional[int] = None,
  ) -> CaseState:
    """Create a new case with generated patient."""

    patient = self.generate_patient(
      condition_key=condition_key,
      learner_level=learner_level,
    )

    return CaseState(
      patient=patient,
      learner_level=learner_level,
      time_constraint=time_constraint,
    )

  def get_condition_info(self, condition_key: str) -> dict:
    """Get full condition information for tutor context."""
    return self.conditions.get(condition_key, {})


# Singleton instance
_generator: Optional[CaseGenerator] = None


def get_generator() -> CaseGenerator:
  """Get the case generator singleton."""
  global _generator
  if _generator is None:
    _generator = CaseGenerator()
  return _generator
