"""Well-child case generator using Claude + well-child teaching frameworks."""

import random
import json
from pathlib import Path
from typing import Optional
import yaml
import anthropic

from ..config import get_settings
from .models import (
  GeneratedPatient,
  CaseState,
  CasePhase,
  LearnerLevel,
  VisitType,
)


FRAMEWORKS_DIR = Path(__file__).parent.parent.parent / "knowledge" / "frameworks"


class WellChildGenerator:
  """Generates well-child cases using Claude + well-child frameworks."""

  def __init__(self):
    self.frameworks: dict = {}
    self._load_frameworks()

  def _get_client(self):
    """Lazy-load the Anthropic client."""
    settings = get_settings()
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)

  def _get_model(self):
    """Get the Claude model name."""
    return get_settings().claude_model

  def _load_frameworks(self):
    """Load well-child framework YAML files."""
    if not FRAMEWORKS_DIR.exists():
      return
    for yaml_file in FRAMEWORKS_DIR.glob("well_child_*.yaml"):
      with open(yaml_file) as f:
        data = yaml.safe_load(f)
        if data and "topic" in data:
          self.frameworks[yaml_file.stem] = data

  def list_visit_ages(self) -> list[dict]:
    """List available well-child visit ages."""
    ages = []
    for key, fw in self.frameworks.items():
      ages.append({
        "key": key,
        "topic": fw.get("topic"),
        "visit_age_months": fw.get("visit_age_months"),
        "category": fw.get("category"),
      })
    return sorted(ages, key=lambda a: a.get("visit_age_months", 0))

  def get_framework(self, key: str) -> Optional[dict]:
    """Get a well-child framework by key."""
    return self.frameworks.get(key)

  def get_framework_by_age(self, age_months: int) -> Optional[tuple[str, dict]]:
    """Get framework by visit age in months."""
    for key, fw in self.frameworks.items():
      if fw.get("visit_age_months") == age_months:
        return (key, fw)
    return None

  async def generate_case(
    self,
    visit_age_months: int,
    learner_level: LearnerLevel = LearnerLevel.STUDENT,
    time_constraint: Optional[int] = None,
  ) -> CaseState:
    """Generate a well-child case for a specific visit age."""
    result = self.get_framework_by_age(visit_age_months)
    if result is None:
      raise ValueError(f"No well-child framework for {visit_age_months} months")

    key, framework = result

    # Roll for incidental finding
    incidental = self._roll_incidental_finding(framework)

    # Generate patient with Claude
    patient = await self._generate_patient(
      framework=framework,
      condition_key=key,
      learner_level=learner_level,
      incidental_finding=incidental,
    )

    return CaseState(
      patient=patient,
      learner_level=learner_level,
      visit_type=VisitType.WELL_CHILD,
      phase=CasePhase.INTRO,
      time_constraint=time_constraint,
    )

  def _roll_incidental_finding(self, framework: dict) -> Optional[dict]:
    """Roll dice on possible incidental findings."""
    findings = framework.get("possible_findings", [])
    if not findings:
      return None
    for finding in findings:
      prob = finding.get("probability", 0.0)
      if random.random() < prob:
        return finding
    return None

  async def _generate_patient(
    self,
    framework: dict,
    condition_key: str,
    learner_level: LearnerLevel,
    incidental_finding: Optional[dict] = None,
  ) -> GeneratedPatient:
    """Use Claude to generate a well-child patient."""
    visit_age = framework.get("visit_age_months", 12)
    parent_styles = framework.get("parent_styles", ["concerned first-time parent"])
    milestones = framework.get("expected_milestones", {})
    immunizations = framework.get("immunizations_due", [])

    finding_instruction = ""
    if incidental_finding:
      finding_instruction = f"""
IMPORTANT: This case includes an incidental finding:
- Finding: {incidental_finding.get('description', '')}
- It should surface naturally during the exam or parent questions phase.
- Include subtle hints in the patient data but don't make it obvious.
"""

    age_unit = "months" if visit_age < 24 else "years"
    age_display = visit_age if visit_age < 24 else visit_age // 12

    prompt = f"""Generate a realistic pediatric patient for a {framework.get('topic')} visit.

## Visit Context
- Visit type: Well-child check
- Visit age: {visit_age} months
- This is a HEALTHY child coming for a routine check

## Parent Styles (pick one): {', '.join(parent_styles)}

## Expected Milestones for This Age
{json.dumps(milestones, indent=2)}

## Immunizations Due
{json.dumps(immunizations, indent=2)}

{finding_instruction}

## Your Task
Generate a healthy patient with realistic details. The child should be mostly
developing normally for their age, with natural variation (not every milestone
perfectly on time).

Return ONLY valid JSON:
{{
  "name": "Child's first and last name",
  "age": {age_display},
  "age_unit": "{age_unit}",
  "sex": "male|female",
  "weight_kg": <age-appropriate weight>,
  "parent_name": "Parent's first name",
  "parent_style": "one of the parent styles above",
  "growth_data": {{
    "weight_percentile": <5-95>,
    "length_percentile": <5-95>,
    "head_circumference_percentile": <5-95>,
    "weight_trend": "stable|crossing_up|crossing_down",
    "previous_weight_percentile": <5-95>
  }},
  "milestones": {{
    "gross_motor": ["milestones met"],
    "fine_motor": ["milestones met"],
    "language": ["milestones met"],
    "social_emotional": ["milestones met"],
    "cognitive": ["milestones met"],
    "concerns": ["any milestone NOT met, or empty array"]
  }},
  "immunization_history": ["vaccines already received, if any gaps note them"],
  "vitals": {{
    "temp_f": <97.5-99.0>,
    "heart_rate": <age-appropriate>,
    "respiratory_rate": <age-appropriate>,
    "spo2": <98-100>
  }},
  "exam_findings": [
    {{"system": "system", "finding": "normal or abnormal finding"}},
    ...include 4-6 systems with mostly normal findings
  ],
  "parent_concerns": ["any specific concerns the parent raises, or empty"],
  "social_context": "Brief family/social context"
}}"""

    client = self._get_client()
    response = client.messages.create(
      model=self._get_model(),
      max_tokens=1024,
      messages=[{"role": "user", "content": prompt}]
    )

    content = response.content[0].text.strip()
    if content.startswith("```"):
      content = content.split("\n", 1)[1]
    if content.endswith("```"):
      content = content.rsplit("\n", 1)[0]
    content = content.strip()

    try:
      data = json.loads(content)
    except json.JSONDecodeError:
      return self._fallback_patient(framework, condition_key)

    return GeneratedPatient(
      name=data.get("name", "Baby Smith"),
      age=data.get("age", age_display),
      age_unit=data.get("age_unit", age_unit),
      sex=data.get("sex", "female"),
      weight_kg=data.get("weight_kg", 5.0),
      chief_complaint=None,
      parent_name=data.get("parent_name", "Parent"),
      parent_style=data.get("parent_style", "concerned"),
      condition_key=condition_key,
      condition_display=framework.get("topic", "Well-Child Visit"),
      symptoms=[],
      vitals=data.get("vitals", {"temp_f": 98.6, "heart_rate": 120, "respiratory_rate": 30, "spo2": 99}),
      exam_findings=data.get("exam_findings", []),
      visit_age_months=visit_age,
      growth_data=data.get("growth_data"),
      milestones=data.get("milestones"),
      immunization_history=data.get("immunization_history"),
      incidental_finding=incidental_finding,
    )

  def _fallback_patient(self, framework: dict, condition_key: str) -> GeneratedPatient:
    """Fallback patient if Claude generation fails."""
    visit_age = framework.get("visit_age_months", 12)
    return GeneratedPatient(
      name="Jordan Smith",
      age=visit_age if visit_age < 24 else visit_age // 12,
      age_unit="months" if visit_age < 24 else "years",
      sex=random.choice(["male", "female"]),
      weight_kg=10.0,
      chief_complaint=None,
      parent_name="Parent",
      parent_style="concerned",
      condition_key=condition_key,
      condition_display=framework.get("topic", "Well-Child Visit"),
      symptoms=[],
      vitals={"temp_f": 98.6, "heart_rate": 120, "respiratory_rate": 30, "spo2": 99},
      exam_findings=[],
      visit_age_months=visit_age,
    )


_well_child_generator: Optional[WellChildGenerator] = None


def get_well_child_generator() -> WellChildGenerator:
  """Get the well-child generator singleton."""
  global _well_child_generator
  if _well_child_generator is None:
    _well_child_generator = WellChildGenerator()
  return _well_child_generator
