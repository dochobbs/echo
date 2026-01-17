"""Dynamic case generator using Claude + lightweight teaching frameworks."""

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
  LearnerLevel,
  CaseSeverity,
  AgeBracket,
  CasePresentation,
  CaseComplexity,
)


# Frameworks directory
FRAMEWORKS_DIR = Path(__file__).parent.parent.parent / "knowledge" / "frameworks"


class DynamicCaseGenerator:
  """Generates cases dynamically using Claude + teaching frameworks."""

  def __init__(self):
    self.frameworks: dict = {}
    self._load_frameworks()
    settings = get_settings()
    self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    self.model = settings.claude_model

  def _load_frameworks(self):
    """Load all framework YAML files."""
    if not FRAMEWORKS_DIR.exists():
      return

    for yaml_file in FRAMEWORKS_DIR.glob("*.yaml"):
      if yaml_file.name.startswith("_"):
        continue  # Skip schema/template files
      with open(yaml_file) as f:
        data = yaml.safe_load(f)
        if data and "topic" in data:
          # Use filename as key
          key = yaml_file.stem
          self.frameworks[key] = data

  def list_conditions(self) -> list[dict]:
    """List available conditions with basic info."""
    return [
      {
        "key": key,
        "topic": fw.get("topic"),
        "category": fw.get("category"),
        "age_range": fw.get("age_range_months"),
      }
      for key, fw in self.frameworks.items()
    ]

  async def generate_case(
    self,
    condition_key: Optional[str] = None,
    learner_level: LearnerLevel = LearnerLevel.STUDENT,
    time_constraint: Optional[int] = None,
    severity: Optional[CaseSeverity] = None,
    age_bracket: Optional[AgeBracket] = None,
    presentation: Optional[CasePresentation] = None,
    complexity: Optional[CaseComplexity] = None,
  ) -> CaseState:
    """Generate a case dynamically using Claude.

    Args:
      condition_key: Specific condition or None for random
      learner_level: Student, resident, etc.
      time_constraint: Minutes available for case
      severity: mild/moderate/severe or None for random
      age_bracket: neonate/infant/toddler/child/adolescent or None for framework default
      presentation: typical/atypical/early/late or None for random
      complexity: straightforward/nuanced/challenging or None (defaults to learner level)
    """
    # Select framework
    if condition_key is None:
      available = list(self.frameworks.keys())
      if not available:
        raise ValueError("No frameworks available")
      condition_key = random.choice(available)

    framework = self.frameworks.get(condition_key)
    if not framework:
      raise ValueError(f"Unknown condition: {condition_key}")

    # Generate patient with Claude
    patient = await self._generate_patient(
      framework=framework,
      learner_level=learner_level,
      severity=severity,
      age_bracket=age_bracket,
      presentation=presentation,
      complexity=complexity,
    )

    return CaseState(
      patient=patient,
      learner_level=learner_level,
      time_constraint=time_constraint,
    )

  async def _generate_patient(
    self,
    framework: dict,
    learner_level: LearnerLevel,
    severity: Optional[CaseSeverity] = None,
    age_bracket: Optional[AgeBracket] = None,
    presentation: Optional[CasePresentation] = None,
    complexity: Optional[CaseComplexity] = None,
  ) -> GeneratedPatient:
    """Use Claude to generate a realistic patient based on the framework."""

    age_range = framework.get("age_range_months", [12, 60])
    parent_styles = framework.get("parent_styles", ["anxious", "experienced"])

    # Build age guidance based on age_bracket parameter
    age_guidance = f"{age_range[0]} to {age_range[1]} months"
    if age_bracket:
      age_brackets_months = {
        AgeBracket.NEONATE: (0, 1),      # 0-28 days -> use days
        AgeBracket.INFANT: (1, 12),
        AgeBracket.TODDLER: (12, 36),
        AgeBracket.CHILD: (36, 144),     # 3-12 years
        AgeBracket.ADOLESCENT: (144, 216),  # 12-18 years
      }
      bracket_range = age_brackets_months.get(age_bracket, (age_range[0], age_range[1]))
      age_guidance = f"{bracket_range[0]} to {bracket_range[1]} months (age bracket: {age_bracket.value})"

    # Build variant parameters section
    variant_section = f"""## Case Variant Parameters
- Severity: {severity.value if severity else "your choice - vary between mild/moderate/severe"}
- Age bracket: {age_bracket.value if age_bracket else "within framework range"}
- Presentation: {presentation.value if presentation else "your choice - can be typical or atypical"}
- Complexity: {complexity.value if complexity else f"appropriate for {learner_level.value} level"}

{"IMPORTANT: This is a " + severity.value.upper() + " case - adjust vitals, symptoms, and findings accordingly." if severity else ""}
{"IMPORTANT: Use " + presentation.value.upper() + " presentation features." if presentation else ""}
"""

    prompt = f"""Generate a realistic pediatric patient for a case about {framework.get('topic')}.

## Framework Context
- Condition: {framework.get('topic')}
- Category: {framework.get('category')}
- Age guidance: {age_guidance}
- Parent styles to choose from: {', '.join(parent_styles)}

{variant_section}

## Key Clinical Features (use these to inform presentation)
Teaching goals: {json.dumps(framework.get('teaching_goals', []))}
Common mistakes learners make: {json.dumps(framework.get('common_mistakes', []))}
Red flags to potentially include: {json.dumps(framework.get('red_flags', [])[:2])}

## Your Task
Generate a patient with realistic, varied details. Make them feel like a real person, not a textbook case.

Return ONLY valid JSON with this exact structure:
{{
  "name": "Child's first and last name",
  "age": <number>,
  "age_unit": "days|weeks|months|years",
  "sex": "male|female",
  "weight_kg": <number appropriate for age>,
  "chief_complaint": "What the parent says when they call/arrive - in their voice, natural language",
  "parent_name": "Parent's first name",
  "parent_style": "one of: {', '.join(parent_styles)}",
  "symptoms": ["list", "of", "3-5", "symptoms", "present"],
  "symptom_details": {{
    "duration_days": <number>,
    "severity": "mild|moderate|severe",
    "progression": "improving|stable|worsening"
  }},
  "vitals": {{
    "temp_f": <number 98-104>,
    "heart_rate": <age-appropriate>,
    "respiratory_rate": <age-appropriate>,
    "spo2": <92-100>
  }},
  "exam_findings": [
    {{"system": "system name", "finding": "what you see/hear"}},
    ...
  ],
  "relevant_history": ["any", "relevant", "past", "history"],
  "social_context": "Brief family/social context that adds realism"
}}

Make the patient realistic and varied:
- Don't always use the most classic presentation
- Include some incidental normal findings
- Make the parent voice authentic
- Add realistic social context"""

    response = self.client.messages.create(
      model=self.model,
      max_tokens=1024,
      messages=[{"role": "user", "content": prompt}]
    )

    # Parse the response
    content = response.content[0].text.strip()
    # Clean any markdown code blocks
    if content.startswith("```"):
      content = content.split("\n", 1)[1]
    if content.endswith("```"):
      content = content.rsplit("\n", 1)[0]
    content = content.strip()

    try:
      data = json.loads(content)
    except json.JSONDecodeError:
      # Fallback to basic patient
      return self._fallback_patient(framework)

    # Build GeneratedPatient
    return GeneratedPatient(
      name=data.get("name", "Alex Smith"),
      age=data.get("age", 24),
      age_unit=data.get("age_unit", "months"),
      sex=data.get("sex", "male"),
      weight_kg=data.get("weight_kg", 12.0),
      chief_complaint=data.get("chief_complaint", f"My child has {framework.get('topic')}"),
      parent_name=data.get("parent_name", "Mom"),
      parent_style=data.get("parent_style", "anxious"),
      condition_key=list(self.frameworks.keys())[list(self.frameworks.values()).index(framework)],
      condition_display=framework.get("topic", "Unknown"),
      symptoms=data.get("symptoms", []),
      vitals=data.get("vitals", {"temp_f": 99.0, "heart_rate": 120, "respiratory_rate": 24, "spo2": 98}),
      exam_findings=data.get("exam_findings", []),
    )

  def _fallback_patient(self, framework: dict) -> GeneratedPatient:
    """Generate a basic patient if Claude fails."""
    age_range = framework.get("age_range_months", [12, 60])
    age_months = random.randint(age_range[0], age_range[1])

    if age_months < 24:
      age = age_months
      age_unit = "months"
    else:
      age = age_months // 12
      age_unit = "years"

    return GeneratedPatient(
      name="Jordan Smith",
      age=age,
      age_unit=age_unit,
      sex=random.choice(["male", "female"]),
      weight_kg=10.0,
      chief_complaint=f"My child has symptoms of {framework.get('topic')}",
      parent_name="Parent",
      parent_style="anxious",
      condition_key="unknown",
      condition_display=framework.get("topic", "Unknown"),
      symptoms=["fever", "fussiness"],
      vitals={"temp_f": 100.5, "heart_rate": 120, "respiratory_rate": 24, "spo2": 98},
      exam_findings=[],
    )

  def get_framework(self, condition_key: str) -> dict:
    """Get the teaching framework for a condition."""
    return self.frameworks.get(condition_key, {})


# Singleton instance
_dynamic_generator: Optional[DynamicCaseGenerator] = None


def get_dynamic_generator() -> DynamicCaseGenerator:
  """Get the dynamic case generator singleton."""
  global _dynamic_generator
  if _dynamic_generator is None:
    _dynamic_generator = DynamicCaseGenerator()
  return _dynamic_generator
