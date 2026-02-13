# Well-Child Visit Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add pediatric well-child checks as a first-class case type alongside existing sick visits.

**Architecture:** Extend the existing case system with a `visit_type` discriminator. Well-child cases use different phases (growth_review, developmental_screening, etc.), different frameworks (organized by visit age), and different debrief scoring (domain completeness vs diagnostic accuracy). All changes are additive — sick visits untouched.

**Tech Stack:** Python/FastAPI (backend), React 18/TypeScript (frontend), YAML (frameworks), Claude API (generation + tutoring)

**Design Reference:** `docs/plans/2026-02-12-well-child-visits-design.md`

---

## Task 1: Extend Case Models

**Files:**
- Modify: `src/cases/models.py`
- Test: `tests/test_models.py`

**Step 1: Write failing tests for new models**

Add to `tests/test_models.py`:

```python
from src.cases.models import (
  VisitType, CasePhase, CaseState, GeneratedPatient,
  StartCaseRequest, DebriefData, WellChildScores,
)


def test_visit_type_enum():
  """VisitType has sick and well_child."""
  assert VisitType.SICK == "sick"
  assert VisitType.WELL_CHILD == "well_child"


def test_well_child_phases_exist():
  """Well-child phases are in CasePhase."""
  assert CasePhase.GROWTH_REVIEW == "growth_review"
  assert CasePhase.DEVELOPMENTAL_SCREENING == "developmental_screening"
  assert CasePhase.ANTICIPATORY_GUIDANCE == "anticipatory_guidance"
  assert CasePhase.IMMUNIZATIONS == "immunizations"
  assert CasePhase.PARENT_QUESTIONS == "parent_questions"


def test_generated_patient_optional_chief_complaint():
  """Well-child patients have no chief complaint."""
  patient = GeneratedPatient(
    name="Test Baby",
    age=2,
    age_unit="months",
    sex="female",
    weight_kg=5.0,
    parent_name="Mom",
    parent_style="anxious",
    condition_key="well_child_2mo",
    condition_display="2 Month Well-Child Visit",
    symptoms=[],
    vitals={"temp_f": 98.6},
    exam_findings=[],
    visit_age_months=2,
  )
  assert patient.chief_complaint is None
  assert patient.visit_age_months == 2


def test_case_state_well_child_defaults():
  """CaseState defaults to sick visit, well-child fields empty."""
  patient = GeneratedPatient(
    name="Test", age=2, age_unit="months", sex="male",
    weight_kg=5.0, chief_complaint="fever",
    parent_name="Mom", parent_style="anxious",
    condition_key="bronchiolitis", condition_display="Bronchiolitis",
    symptoms=["cough"], vitals={"temp_f": 101.0}, exam_findings=[],
  )
  state = CaseState(patient=patient)
  assert state.visit_type == VisitType.SICK
  assert state.growth_reviewed is False
  assert state.milestones_assessed == []
  assert state.guidance_topics_covered == []


def test_case_state_well_child_type():
  """CaseState can be set to well_child."""
  patient = GeneratedPatient(
    name="Baby", age=4, age_unit="months", sex="female",
    weight_kg=6.5, parent_name="Dad", parent_style="experienced",
    condition_key="well_child_4mo",
    condition_display="4 Month Well-Child Visit",
    symptoms=[], vitals={"temp_f": 98.6}, exam_findings=[],
    visit_age_months=4,
  )
  state = CaseState(
    patient=patient,
    visit_type=VisitType.WELL_CHILD,
    phase=CasePhase.GROWTH_REVIEW,
  )
  assert state.visit_type == VisitType.WELL_CHILD
  assert state.phase == CasePhase.GROWTH_REVIEW


def test_start_case_request_well_child():
  """StartCaseRequest accepts well_child visit type."""
  req = StartCaseRequest(
    visit_type=VisitType.WELL_CHILD,
    visit_age_months=12,
    learner_level="resident",
  )
  assert req.visit_type == VisitType.WELL_CHILD
  assert req.visit_age_months == 12


def test_well_child_scores_model():
  """WellChildScores has all six domains."""
  scores = WellChildScores(
    growth_interpretation={"score": 8, "feedback": "Good trajectory analysis"},
    milestone_assessment={"score": 7, "feedback": "Covered most domains"},
    exam_thoroughness={"score": 9, "feedback": "Age-appropriate exam"},
    anticipatory_guidance={"score": 6, "feedback": "Missed sleep safety"},
    immunization_knowledge={"score": 10, "feedback": "Perfect"},
    communication_skill={"score": 8, "feedback": "Warm and clear"},
  )
  assert scores.growth_interpretation["score"] == 8


def test_debrief_data_well_child_scores():
  """DebriefData can include well_child_scores."""
  debrief = DebriefData(
    summary="Good visit",
    well_child_scores=WellChildScores(
      growth_interpretation={"score": 8, "feedback": "Good"},
      milestone_assessment={"score": 7, "feedback": "Good"},
      exam_thoroughness={"score": 9, "feedback": "Good"},
      anticipatory_guidance={"score": 6, "feedback": "OK"},
      immunization_knowledge={"score": 10, "feedback": "Great"},
      communication_skill={"score": 8, "feedback": "Good"},
    ),
  )
  assert debrief.well_child_scores is not None
  assert debrief.well_child_scores.immunization_knowledge["score"] == 10
```

**Step 2: Run tests to verify they fail**

Run: `cd /Users/dochobbs/Downloads/Consult/MedEd/echo && python -m pytest tests/test_models.py -v`
Expected: FAIL — `VisitType`, `WellChildScores` not importable, `visit_age_months` not a field

**Step 3: Update models.py**

In `src/cases/models.py`, make these changes:

1. Add `VisitType` enum after `CasePhase`:

```python
class VisitType(str, Enum):
  """Type of clinical encounter."""
  SICK = "sick"
  WELL_CHILD = "well_child"
```

2. Add well-child phases to `CasePhase`:

```python
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
```

3. Make `chief_complaint` optional in `GeneratedPatient`, add well-child fields:

```python
class GeneratedPatient(BaseModel):
  """A generated patient for a case."""
  id: str = Field(default_factory=lambda: str(uuid.uuid4()))
  name: str
  age: int
  age_unit: str = "months"
  sex: str
  weight_kg: float
  chief_complaint: Optional[str] = None
  parent_name: str
  parent_style: str
  condition_key: str
  condition_display: str
  symptoms: list[str]
  vitals: dict[str, float]
  exam_findings: list[dict]
  # Well-child specific
  visit_age_months: Optional[int] = None
  growth_data: Optional[dict] = None
  milestones: Optional[dict] = None
  immunization_history: Optional[list] = None
  incidental_finding: Optional[dict] = None
```

4. Add `visit_type` and well-child tracking to `CaseState`:

```python
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
  # Shared
  hints_given: int = 0
  teaching_moments: list[str] = Field(default_factory=list)
  started_at: datetime = Field(default_factory=datetime.now)
  time_constraint: Optional[int] = None
  conversation: list[dict] = Field(default_factory=list)
```

5. Add `visit_type` and `visit_age_months` to `StartCaseRequest`:

```python
class StartCaseRequest(BaseModel):
  """Request to start a new case."""
  learner_level: LearnerLevel = LearnerLevel.STUDENT
  condition_key: Optional[str] = None
  time_constraint: Optional[int] = None
  visit_type: VisitType = VisitType.SICK
  visit_age_months: Optional[int] = None
  severity: Optional[CaseSeverity] = None
  age_bracket: Optional[AgeBracket] = None
  presentation: Optional[CasePresentation] = None
  complexity: Optional[CaseComplexity] = None
```

6. Add `WellChildScores` model and extend `DebriefData`:

```python
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
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/dochobbs/Downloads/Consult/MedEd/echo && python -m pytest tests/test_models.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add src/cases/models.py tests/test_models.py
git commit -m "FEATURE: Add well-child visit types, phases, and model extensions"
```

---

## Task 2: Create Well-Child Framework Schema and First 3 Frameworks

**Files:**
- Create: `knowledge/frameworks/_well_child_schema.yaml`
- Create: `knowledge/frameworks/well_child_2mo.yaml`
- Create: `knowledge/frameworks/well_child_12mo.yaml`
- Create: `knowledge/frameworks/well_child_adolescent.yaml`

**Step 1: Create the well-child schema file**

Create `knowledge/frameworks/_well_child_schema.yaml` with the full schema definition.
Use the design doc section 2 for reference. The file starts with `_` so the loader skips it
(consistent with existing `_schema.yaml`).

**Step 2: Create `well_child_2mo.yaml`**

Use the verified data from the research. This is the first big vaccine visit. Include:
- `visit_type: well_child`
- `visit_age_months: 2`
- `teaching_goals` (4-5 items)
- `expected_milestones` by domain (CDC 2022, 75th percentile)
- `screening_tools` (maternal depression EPDS)
- `anticipatory_guidance` by category (safety, nutrition, development, behavior, sleep)
- `immunizations_due` with CVX codes (HepB #2, RV #1, DTaP #1, Hib #1, PCV20 #1, IPV #1)
- `physical_exam_focus` (fontanelle, red reflex, hips, heart)
- `common_mistakes` (5 items)
- `possible_findings` with probability and framework_link
- `parent_styles` (4 styles)
- `sources` (AAP Bright Futures, CDC)

**Step 3: Create `well_child_12mo.yaml`**

The 12-month visit — MMR/varicella/HepA, bottle weaning, walking assessment, lead/anemia
screening. Follow same schema.

**Step 4: Create `well_child_adolescent.yaml`**

The adolescent visit — Tdap, HPV, MenACWY, HEEADSSS, depression/substance screening,
Tanner staging. This is the most different from infant visits.

**Step 5: Verify YAML files parse correctly**

Run: `cd /Users/dochobbs/Downloads/Consult/MedEd/echo && python -c "import yaml; [yaml.safe_load(open(f'knowledge/frameworks/{f}')) for f in ['well_child_2mo.yaml', 'well_child_12mo.yaml', 'well_child_adolescent.yaml']]; print('All valid')"`
Expected: "All valid"

**Step 6: Commit**

```bash
git add knowledge/frameworks/_well_child_schema.yaml knowledge/frameworks/well_child_2mo.yaml knowledge/frameworks/well_child_12mo.yaml knowledge/frameworks/well_child_adolescent.yaml
git commit -m "FEATURE: Add well-child framework schema and first 3 frameworks (2mo, 12mo, adolescent)"
```

---

## Task 3: Create Remaining 10 Well-Child Frameworks

**Files:**
- Create: `knowledge/frameworks/well_child_newborn.yaml`
- Create: `knowledge/frameworks/well_child_4mo.yaml`
- Create: `knowledge/frameworks/well_child_6mo.yaml`
- Create: `knowledge/frameworks/well_child_9mo.yaml`
- Create: `knowledge/frameworks/well_child_15mo.yaml`
- Create: `knowledge/frameworks/well_child_18mo.yaml`
- Create: `knowledge/frameworks/well_child_24mo.yaml`
- Create: `knowledge/frameworks/well_child_3yr.yaml`
- Create: `knowledge/frameworks/well_child_4yr.yaml`
- Create: `knowledge/frameworks/well_child_5yr.yaml`

**Step 1: Create all 10 framework files**

Follow the same schema as Task 2. Use the verified clinical data from the design doc
(sections 3-5) for each visit age. Key data per visit:

| Visit | Key Vaccines | Key Screenings | Key Guidance |
|-------|-------------|----------------|--------------|
| Newborn | HepB #1, Nirsevimab (RSV) | Metabolic screen, CCHD, hearing, bilirubin | Safe sleep, feeding, cord care, when to call |
| 4mo | RV #2, DTaP #2, Hib #2, PCV20 #2, IPV #2 | Maternal depression | Strabismus should resolve, intro solids discussion |
| 6mo | HepB #3, RV #3 (RV5), DTaP #3, Hib #3, PCV20 #3, IPV #3, Flu #1 | Maternal depression (last), oral health, fluoride | Complementary foods, allergenic food intro, dental home |
| 9mo | Catch-up only, Flu #2 if first season | ASQ-3 (developmental) | Finger foods, childproofing, separation anxiety |
| 15mo | DTaP #4, catch-up MMR/Var/HepA/PCV20/Hib | None specific | Walking milestone (CDC 2022), limit-setting, tantrums |
| 18mo | DTaP #4 (if not at 15mo), HepA #2, HepB/IPV catch-up | ASQ-3, M-CHAT-R/F (autism) | Screen time (<18mo avoid), toilet readiness |
| 24mo | HepA #2 catch-up, Flu | M-CHAT follow-up, lead, BMI starts | Toilet training, low-fat milk, CDC growth charts |
| 3yr | Flu only | BP starts, vision (if cooperative), ASQ-3 at 30mo | Screen time 1hr/day, preschool readiness |
| 4yr | DTaP #5, IPV #4, MMR #2, Var #2, Flu | BP, vision (Snellen), hearing (audiometry) | School readiness, bicycle helmet, swim safety |
| 5yr | Catch-up 4yr vaccines, Flu | BP, vision, hearing | Kindergarten readiness, independence, 60min activity |

Each file follows `_well_child_schema.yaml` exactly.

**Step 2: Verify all framework files parse**

Run: `cd /Users/dochobbs/Downloads/Consult/MedEd/echo && python -c "
import yaml
from pathlib import Path
wc_files = sorted(Path('knowledge/frameworks').glob('well_child_*.yaml'))
for f in wc_files:
    yaml.safe_load(open(f))
    print(f'  OK: {f.name}')
print(f'Total: {len(wc_files)} well-child frameworks')
"`
Expected: 13 files, all OK

**Step 3: Commit**

```bash
git add knowledge/frameworks/well_child_*.yaml
git commit -m "FEATURE: Add remaining 10 well-child frameworks (newborn through 5yr)"
```

---

## Task 4: Update Framework Loader

**Files:**
- Modify: `src/frameworks/loader.py`
- Test: `tests/test_framework_loader.py` (create)

**Step 1: Write failing tests**

Create `tests/test_framework_loader.py`:

```python
"""Test framework loader with well-child support."""

import pytest
from src.frameworks.loader import (
  load_frameworks, get_framework, get_frameworks_by_category,
  get_well_child_frameworks, get_well_child_by_age,
)


def test_load_includes_well_child():
  """Loader picks up well_child framework files."""
  frameworks = load_frameworks(reload=True)
  wc_keys = [k for k in frameworks if k.startswith("well_child_")]
  assert len(wc_keys) == 13


def test_get_well_child_frameworks():
  """get_well_child_frameworks returns only well-child frameworks."""
  wc = get_well_child_frameworks()
  assert len(wc) == 13
  for fw in wc:
    assert fw.get("visit_type") == "well_child" or fw.get("category") == "well_child"


def test_get_well_child_by_age():
  """get_well_child_by_age returns correct framework."""
  fw = get_well_child_by_age(2)
  assert fw is not None
  assert fw.get("visit_age_months") == 2
  assert "teaching_goals" in fw


def test_get_well_child_by_age_not_found():
  """get_well_child_by_age returns None for invalid age."""
  fw = get_well_child_by_age(7)  # No 7-month well-child visit
  assert fw is None


def test_get_frameworks_by_category_well_child():
  """get_frameworks_by_category works for well_child."""
  wc = get_frameworks_by_category("well_child")
  assert len(wc) == 13
```

**Step 2: Run tests to verify they fail**

Run: `cd /Users/dochobbs/Downloads/Consult/MedEd/echo && python -m pytest tests/test_framework_loader.py -v`
Expected: FAIL — `get_well_child_frameworks`, `get_well_child_by_age` don't exist

**Step 3: Add well-child methods to loader.py**

Add to `src/frameworks/loader.py`:

```python
def get_well_child_frameworks() -> list[dict]:
    """Get all well-child visit frameworks.

    Returns:
        List of well-child frameworks with their keys
    """
    if not _loaded:
        load_frameworks()

    return [
        {"key": k, **v}
        for k, v in FRAMEWORKS.items()
        if v.get("category") == "well_child"
    ]


def get_well_child_by_age(age_months: int) -> Optional[dict]:
    """Get well-child framework for a specific visit age.

    Args:
        age_months: Visit age in months (0 for newborn)

    Returns:
        Framework data or None if no matching visit age
    """
    if not _loaded:
        load_frameworks()

    for key, fw in FRAMEWORKS.items():
        if fw.get("category") == "well_child" and fw.get("visit_age_months") == age_months:
            return fw

    return None
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/dochobbs/Downloads/Consult/MedEd/echo && python -m pytest tests/test_framework_loader.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add src/frameworks/loader.py tests/test_framework_loader.py
git commit -m "FEATURE: Add well-child framework loader methods"
```

---

## Task 5: Create Well-Child Patient Generator

**Files:**
- Create: `src/cases/well_child_generator.py`
- Test: `tests/test_well_child_generator.py` (create)

**Step 1: Write failing test**

Create `tests/test_well_child_generator.py`:

```python
"""Test well-child patient generator."""

import pytest
from unittest.mock import patch, MagicMock
from src.cases.well_child_generator import WellChildGenerator
from src.cases.models import VisitType, CasePhase


def test_generator_loads_well_child_frameworks():
  """Generator loads only well-child frameworks."""
  gen = WellChildGenerator()
  ages = gen.list_visit_ages()
  assert len(ages) == 13
  assert any(a["visit_age_months"] == 2 for a in ages)
  assert any(a["visit_age_months"] == 0 for a in ages)  # newborn


def test_generator_list_visit_ages_has_required_fields():
  """Each visit age entry has topic, visit_age_months, key."""
  gen = WellChildGenerator()
  for age in gen.list_visit_ages():
    assert "key" in age
    assert "topic" in age
    assert "visit_age_months" in age


def test_generator_get_framework():
  """Can retrieve a specific well-child framework."""
  gen = WellChildGenerator()
  fw = gen.get_framework("well_child_2mo")
  assert fw is not None
  assert fw.get("visit_age_months") == 2
  assert "immunizations_due" in fw
  assert "expected_milestones" in fw
```

**Step 2: Run tests to verify they fail**

Run: `cd /Users/dochobbs/Downloads/Consult/MedEd/echo && python -m pytest tests/test_well_child_generator.py -v`
Expected: FAIL — module not found

**Step 3: Create well_child_generator.py**

Create `src/cases/well_child_generator.py`:

```python
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
    settings = get_settings()
    self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    self.model = settings.claude_model

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
    guidance = framework.get("anticipatory_guidance", {})

    finding_instruction = ""
    if incidental_finding:
      finding_instruction = f"""
IMPORTANT: This case includes an incidental finding:
- Finding: {incidental_finding.get('description', '')}
- It should surface naturally during the exam or parent questions phase.
- Include subtle hints in the patient data but don't make it obvious.
"""

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
  "age": {visit_age},
  "age_unit": "{'months' if visit_age < 24 else 'years'}",
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

    response = self.client.messages.create(
      model=self.model,
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
      age=data.get("age", visit_age),
      age_unit=data.get("age_unit", "months"),
      sex=data.get("sex", "female"),
      weight_kg=data.get("weight_kg", 5.0),
      chief_complaint=None,  # Well-child has no chief complaint
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
      age=visit_age,
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
```

**Step 4: Run tests to verify they pass**

Run: `cd /Users/dochobbs/Downloads/Consult/MedEd/echo && python -m pytest tests/test_well_child_generator.py -v`
Expected: ALL PASS

**Step 5: Commit**

```bash
git add src/cases/well_child_generator.py tests/test_well_child_generator.py
git commit -m "FEATURE: Add well-child patient generator with incidental finding support"
```

---

## Task 6: Create Well-Child Tutor Prompts

**Files:**
- Create: `src/prompts/well_child.md`
- Create: `src/prompts/well_child_debrief.md`

**Step 1: Create `src/prompts/well_child.md`**

Write the well-child teaching mode prompt. Full content from design doc section 6.
Key sections: phase-specific teaching guidance, role transitions for well-child context,
how to handle incidental findings, parent interaction style.

**Step 2: Create `src/prompts/well_child_debrief.md`**

Write the well-child debrief scoring prompt. Instructs Claude to score across 6 domains
(0-10 each): growth_interpretation, milestone_assessment, exam_thoroughness,
anticipatory_guidance, immunization_knowledge, communication_skill.

JSON output format matching `WellChildScores` model.

**Step 3: Verify prompt files load**

Run: `cd /Users/dochobbs/Downloads/Consult/MedEd/echo && python -c "
from pathlib import Path
for name in ['well_child', 'well_child_debrief']:
    p = Path(f'src/prompts/{name}.md')
    assert p.exists(), f'{name}.md not found'
    content = p.read_text()
    assert len(content) > 100, f'{name}.md too short'
    print(f'  OK: {name}.md ({len(content)} chars)')
"`
Expected: Both files exist and have content

**Step 4: Commit**

```bash
git add src/prompts/well_child.md src/prompts/well_child_debrief.md
git commit -m "FEATURE: Add well-child tutor and debrief prompt templates"
```

---

## Task 7: Update Tutor for Well-Child Cases

**Files:**
- Modify: `src/core/tutor.py`

This is the largest code change. The tutor needs to:
1. Load well-child prompts
2. Build different system prompts for well-child cases
3. Detect well-child phases
4. Generate well-child openings
5. Generate well-child debriefs

**Step 1: Add well-child prompt loader**

At top of `tutor.py` (near line 37), add:

```python
@lru_cache
def get_well_child_prompt() -> str:
  """Load and cache the well-child teaching prompt."""
  return load_prompt("well_child")


@lru_cache
def get_well_child_debrief_prompt() -> str:
  """Load and cache the well-child debrief prompt."""
  return load_prompt("well_child_debrief")
```

**Step 2: Add `_build_well_child_system_prompt` method**

Add new method to `Tutor` class (after `_build_case_system_prompt`):

```python
def _build_well_child_system_prompt(self, case_state: "CaseState", framework: dict) -> str:
    """Build system prompt for well-child case teaching."""
    patient = case_state.patient
    well_child_prompt = get_well_child_prompt()

    milestones_text = ""
    if framework.get("expected_milestones"):
      for domain, items in framework["expected_milestones"].items():
        milestones_text += f"\n**{domain}**: {', '.join(items)}"

    immunizations_text = ""
    for vax in framework.get("immunizations_due", []):
      immunizations_text += f"\n- {vax.get('vaccine', '')} (CVX {vax.get('cvx', '')})"

    guidance_text = ""
    for category, items in framework.get("anticipatory_guidance", {}).items():
      guidance_text += f"\n**{category}**: {', '.join(items[:3])}"

    exam_focus_text = ""
    for item in framework.get("physical_exam_focus", []):
      exam_focus_text += f"\n- {item.get('area', '')}: {item.get('detail', '')}"

    incidental_text = ""
    if patient.incidental_finding:
      incidental_text = f"""
### INCIDENTAL FINDING (reveal during exam or parent_questions phase)
- **Finding**: {patient.incidental_finding.get('description', '')}
- **Age relevance**: {patient.incidental_finding.get('age_relevance', '')}
- Present this naturally — don't announce it. Let the learner discover it."""

    return f"""{self.system_prompt}

{well_child_prompt}

## CURRENT WELL-CHILD CASE

### Patient
- **Name**: {patient.name}
- **Visit Age**: {patient.visit_age_months} months
- **Sex**: {patient.sex}
- **Weight**: {patient.weight_kg} kg
- **Parent**: {patient.parent_name} (style: {patient.parent_style})

### Growth Data
{json.dumps(patient.growth_data, indent=2) if patient.growth_data else "Standard growth"}

### Expected Milestones for This Age
{milestones_text}

### Actual Milestone Status
{json.dumps(patient.milestones, indent=2) if patient.milestones else "Typical for age"}

### Immunizations Due at This Visit
{immunizations_text}

### Anticipatory Guidance Topics
{guidance_text}

### Physical Exam Focus Areas
{exam_focus_text}

### Teaching Goals
{chr(10).join(['- ' + g for g in framework.get('teaching_goals', [])])}

### Common Learner Mistakes
{chr(10).join(['- ' + m for m in framework.get('common_mistakes', [])])}

### Screening Tools for This Age
{chr(10).join(['- ' + s.get('tool', '') + ' (' + s.get('when', '') + ')' for s in framework.get('screening_tools', [])])}

{incidental_text}

## Current Phase: {case_state.phase.value}

## WELL-CHILD RULES
1. **No chief complaint** - This child is here for a routine check
2. **Play the parent** - Respond to questions as the parent would
3. **Don't volunteer information** - Let the learner drive the visit
4. **Track what they cover** - Note which guidance topics, milestones, and vaccines they address
5. **Incidental finding** - If present, reveal naturally during appropriate phase
6. **Celebrate thoroughness** - Praise when they remember important screenings or guidance topics"""
```

**Step 3: Update `_build_case_system_prompt` to branch on visit type**

Modify the existing `_build_case_system_prompt` (line 349) to check visit type:

```python
def _build_case_system_prompt(self, case_state: "CaseState", condition_info: dict) -> str:
    """Build a system prompt for case-based teaching."""
    from ..cases.models import VisitType
    if case_state.visit_type == VisitType.WELL_CHILD:
      return self._build_well_child_system_prompt(case_state, condition_info)

    # ... existing sick visit code unchanged ...
```

**Step 4: Add well-child phase detection**

Add `_update_well_child_phase` method:

```python
def _update_well_child_phase(self, message: str, case_state: "CaseState") -> "CaseState":
    """Update well-child case phase based on learner's message."""
    from ..cases.models import CasePhase
    msg_lower = message.lower()

    if case_state.phase == CasePhase.INTRO:
      if any(w in msg_lower for w in ["growth", "weight", "percentile", "chart", "gaining", "length", "head circumference"]):
        case_state.phase = CasePhase.GROWTH_REVIEW
      elif any(w in msg_lower for w in ["milestone", "development", "rolling", "sitting", "walking", "talking", "words"]):
        case_state.phase = CasePhase.DEVELOPMENTAL_SCREENING

    elif case_state.phase == CasePhase.GROWTH_REVIEW:
      if any(w in msg_lower for w in ["milestone", "development", "rolling", "sitting", "walking", "talking", "babbl", "words", "screen"]):
        case_state.phase = CasePhase.DEVELOPMENTAL_SCREENING
        case_state.growth_reviewed = True

    elif case_state.phase == CasePhase.DEVELOPMENTAL_SCREENING:
      if any(w in msg_lower for w in ["examine", "look at", "check", "exam", "heart", "ears", "hips", "lungs", "belly", "reflex"]):
        case_state.phase = CasePhase.EXAM

    elif case_state.phase == CasePhase.EXAM:
      if any(w in msg_lower for w in ["safety", "sleep", "feeding", "nutrition", "car seat", "tummy time", "screen time", "guidance", "counsel", "anticipatory"]):
        case_state.phase = CasePhase.ANTICIPATORY_GUIDANCE

    elif case_state.phase == CasePhase.ANTICIPATORY_GUIDANCE:
      if any(w in msg_lower for w in ["vaccine", "immuniz", "shot", "dtap", "mmr", "pcv", "hep", "flu", "schedule"]):
        case_state.phase = CasePhase.IMMUNIZATIONS

    elif case_state.phase == CasePhase.IMMUNIZATIONS:
      if any(w in msg_lower for w in ["question", "concern", "anything else", "wrap up", "done", "follow up"]):
        case_state.phase = CasePhase.PARENT_QUESTIONS

    return case_state
```

**Step 5: Update `_update_case_phase` to branch on visit type**

Modify existing method (line 608):

```python
def _update_case_phase(self, message: str, case_state: "CaseState") -> "CaseState":
    """Update case phase based on learner's message."""
    from ..cases.models import CasePhase, VisitType
    if case_state.visit_type == VisitType.WELL_CHILD:
      return self._update_well_child_phase(message, case_state)

    # ... existing sick visit code unchanged ...
```

**Step 6: Add well-child phase guidance**

Update `_get_phase_guidance` (line 637) to include well-child phases:

```python
def _get_phase_guidance(self, phase: "CasePhase") -> str:
    from ..cases.models import CasePhase
    guidance = {
      # Existing sick visit phases
      CasePhase.INTRO: "The learner is just starting. Let them take the lead.",
      CasePhase.HISTORY: "They're gathering history. Answer as the parent. Don't volunteer info.",
      CasePhase.EXAM: "They want to examine. Describe findings. Be specific about normal and abnormal.",
      CasePhase.ASSESSMENT: "They're forming an assessment. Listen. Gently probe if differential incomplete.",
      CasePhase.PLAN: "They're making a plan. Validate good choices, question problematic ones.",
      CasePhase.DEBRIEF: "Time to debrief. Summarize strengths and areas to improve.",
      CasePhase.COMPLETE: "The case is complete.",
      # Well-child phases
      CasePhase.GROWTH_REVIEW: "They're reviewing growth. See if they interpret trajectory, not just read numbers.",
      CasePhase.DEVELOPMENTAL_SCREENING: "They're assessing development. See if they cover all domains and know screening tools.",
      CasePhase.ANTICIPATORY_GUIDANCE: "They're counseling the parent. Don't prompt topics — see what they cover. Play the parent with realistic questions.",
      CasePhase.IMMUNIZATIONS: "They're addressing vaccines. See if they know what's due. If parent is hesitant, stay in character.",
      CasePhase.PARENT_QUESTIONS: "The parent has a question or concern. This may include an incidental finding. See how the learner handles it.",
    }
    return guidance.get(phase, "Continue the encounter naturally.")
```

**Step 7: Add well-child opening generation**

Update `generate_case_opening` (line 442) to handle well-child:

```python
async def generate_case_opening(self, case_state: "CaseState", condition_info: dict) -> str:
    """Generate the opening message for a case."""
    from ..cases.models import VisitType
    patient = case_state.patient

    if case_state.visit_type == VisitType.WELL_CHILD:
      prompt = f"""You're starting a well-child visit case with a {case_state.learner_level.value} learner.

The patient is {patient.name}, a {patient.age} {patient.age_unit} old {patient.sex}
here for their {condition_info.get('topic', 'well-child check')}.
The parent ({patient.parent_name}) is here and seems {patient.parent_style}.

Start the encounter:
1. Briefly set the scene (routine well-child visit, you're the attending)
2. Present as the parent bringing in the child for their check-up
3. Mention any specific parent concerns if they have them, otherwise say things are going well
4. End with something that invites them to take the lead on the visit

Keep it natural. No chief complaint — this child is here for a routine visit.
3-4 sentences max from the parent."""
    else:
      # Existing sick visit opening prompt
      prompt = f"""You're starting a new case with a {case_state.learner_level.value} learner.

The patient is {patient.name}, a {patient.age} {patient.age_unit} old {patient.sex}.
The parent ({patient.parent_name}) is bringing them in with this chief complaint:

"{patient.chief_complaint}"

Start the encounter:
1. Briefly set the scene (you're the attending, they're the learner)
2. Present as the parent bringing in the child
3. Give the chief complaint in the parent's voice
4. End with something that invites them to take the lead

Keep it natural and conversational. No more than 3-4 sentences from the parent to start.
This is their first interaction - make it feel welcoming and zero-pressure."""

    system = self._build_case_system_prompt(case_state, condition_info)
    response = self.client.messages.create(
      model=self.model,
      max_tokens=512,
      system=system,
      messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
```

**Step 8: Add well-child debrief generation**

Add `generate_well_child_debrief` method:

```python
async def generate_well_child_debrief(self, case_state: "CaseState", framework: dict) -> dict:
    """Generate well-child debrief with domain scores."""
    patient = case_state.patient
    well_child_debrief_prompt = get_well_child_debrief_prompt()

    prompt = f"""{well_child_debrief_prompt}

## Case Summary
- **Visit**: {framework.get('topic', 'Well-Child Visit')}
- **Patient**: {patient.name}, {patient.age} {patient.age_unit}
- **Learner Level**: {case_state.learner_level.value}

## What the Learner Covered
- **Growth reviewed**: {case_state.growth_reviewed}
- **Milestones assessed**: {', '.join(case_state.milestones_assessed) if case_state.milestones_assessed else 'None documented'}
- **Guidance topics**: {', '.join(case_state.guidance_topics_covered) if case_state.guidance_topics_covered else 'None documented'}
- **Immunizations addressed**: {case_state.immunizations_addressed}
- **Screening tools used**: {', '.join(case_state.screening_tools_used) if case_state.screening_tools_used else 'None'}
- **Parent concerns addressed**: {', '.join(case_state.parent_concerns_addressed) if case_state.parent_concerns_addressed else 'None'}

## Expected at This Visit
- **Teaching goals**: {json.dumps(framework.get('teaching_goals', []))}
- **Immunizations due**: {json.dumps(framework.get('immunizations_due', []))}
- **Screening tools**: {json.dumps(framework.get('screening_tools', []))}
- **Anticipatory guidance**: {json.dumps(framework.get('anticipatory_guidance', {}))}

## Response Format
Return valid JSON only:
{{"summary": "2-3 sentences", "strengths": ["specific strengths"], "areas_for_improvement": ["specific areas"], "missed_items": ["what was missed"], "teaching_points": ["1-3 pearls"], "follow_up_resources": ["optional resources"], "well_child_scores": {{"growth_interpretation": {{"score": 0-10, "feedback": "specific feedback"}}, "milestone_assessment": {{"score": 0-10, "feedback": "..."}}, "exam_thoroughness": {{"score": 0-10, "feedback": "..."}}, "anticipatory_guidance": {{"score": 0-10, "feedback": "..."}}, "immunization_knowledge": {{"score": 0-10, "feedback": "..."}}, "communication_skill": {{"score": 0-10, "feedback": "..."}}}}}}"""

    response = self.client.messages.create(
      model=self.model,
      max_tokens=1500,
      system=self.system_prompt,
      messages=[{"role": "user", "content": prompt}]
    )

    content = clean_json_response(response.content[0].text)
    try:
      return json.loads(content)
    except json.JSONDecodeError:
      return {"summary": "Case complete.", "strengths": [], "areas_for_improvement": [], "missed_items": [], "teaching_points": [], "follow_up_resources": [], "well_child_scores": None}
```

**Step 9: Update `generate_debrief` to branch on visit type**

Modify existing `generate_debrief` (line 652):

```python
async def generate_debrief(self, case_state: "CaseState", condition_info: dict) -> dict:
    """Generate end-of-case debrief."""
    from ..cases.models import VisitType
    if case_state.visit_type == VisitType.WELL_CHILD:
      return await self.generate_well_child_debrief(case_state, condition_info)

    # ... existing sick visit debrief code unchanged ...
```

**Step 10: Commit**

```bash
git add src/core/tutor.py
git commit -m "FEATURE: Add well-child teaching logic to tutor (prompts, phases, debrief)"
```

---

## Task 8: Update Case Router

**Files:**
- Modify: `src/cases/router.py`

**Step 1: Update start endpoint to handle well-child**

Modify `start_dynamic_case` (line 99) and `start_case` (line 150) to check `visit_type`:

In `start_dynamic_case`:
```python
@router.post("/start/dynamic")
async def start_dynamic_case(request: StartCaseRequest) -> CaseResponse:
  from ..core.tutor import Tutor
  from .models import VisitType

  if request.visit_type == VisitType.WELL_CHILD:
    from .well_child_generator import get_well_child_generator
    generator = get_well_child_generator()
    if request.visit_age_months is None:
      raise HTTPException(status_code=400, detail="visit_age_months required for well-child cases")
    case_state = await generator.generate_case(
      visit_age_months=request.visit_age_months,
      learner_level=request.learner_level,
      time_constraint=request.time_constraint,
    )
    framework = generator.get_framework(case_state.patient.condition_key)
  else:
    generator = get_dynamic_generator()
    case_state = await generator.generate_case(
      condition_key=request.condition_key,
      learner_level=request.learner_level,
      time_constraint=request.time_constraint,
      severity=request.severity,
      age_bracket=request.age_bracket,
      presentation=request.presentation,
      complexity=request.complexity,
    )
    framework = generator.get_framework(case_state.patient.condition_key)

  tutor = Tutor()
  opening = await tutor.generate_case_opening(case_state, framework)
  case_state.conversation.append({"role": "echo", "content": opening})
  images = _get_images_for_phase(framework, case_state.phase)

  return CaseResponse(message=opening, case_state=case_state, images=images)
```

**Step 2: Add framework type filter to /frameworks endpoint**

Update `list_frameworks` (line 89):

```python
@router.get("/frameworks")
async def list_frameworks(type: Optional[str] = None):
  """List available teaching frameworks. Filter by type: 'sick', 'well_child', or None for all."""
  if type == "well_child":
    from .well_child_generator import get_well_child_generator
    gen = get_well_child_generator()
    return {"frameworks": gen.list_visit_ages(), "total": len(gen.list_visit_ages())}

  generator = get_dynamic_generator()
  sick_frameworks = generator.list_conditions()

  if type == "sick":
    return {"frameworks": sick_frameworks, "total": len(sick_frameworks)}

  # Return all
  from .well_child_generator import get_well_child_generator
  wc_gen = get_well_child_generator()
  all_frameworks = sick_frameworks + wc_gen.list_visit_ages()
  return {"frameworks": all_frameworks, "total": len(all_frameworks)}
```

**Step 3: Update debrief endpoint to handle well-child scores**

Modify `get_debrief` (line 245) to pass `well_child_scores` through:

```python
debrief = DebriefData(
    summary=debrief_data.get("summary", "Case complete."),
    strengths=debrief_data.get("strengths", []),
    areas_for_improvement=debrief_data.get("areas_for_improvement", []),
    missed_items=debrief_data.get("missed_items", []),
    teaching_points=debrief_data.get("teaching_points", []),
    follow_up_resources=debrief_data.get("follow_up_resources", []),
    well_child_scores=debrief_data.get("well_child_scores"),
)
```

**Step 4: Ensure /case/message uses correct framework source**

In `send_message` (line 194), update to load well-child framework when appropriate:

```python
from .models import VisitType

if case_state.visit_type == VisitType.WELL_CHILD:
    from .well_child_generator import get_well_child_generator
    wc_gen = get_well_child_generator()
    condition_info = wc_gen.get_framework(case_state.patient.condition_key) or {}
else:
    generator = get_generator()
    condition_info = generator.get_condition_info(case_state.patient.condition_key)
```

**Step 5: Commit**

```bash
git add src/cases/router.py
git commit -m "FEATURE: Route well-child cases through API endpoints"
```

---

## Task 9: Update Database Models

**Files:**
- Modify: `src/db_models.py`

**Step 1: Add visit_type and well-child columns to CaseSession**

```python
class CaseSession(Base):
    __tablename__ = "case_sessions"

    # ... existing columns ...
    visit_type = Column(String(50), default="sick")  # "sick" or "well_child"
    visit_age_months = Column(Integer, nullable=True)
    # Well-child tracking
    growth_reviewed = Column(String(10), default="false")
    milestones_assessed = Column(ARRAY(Text), default=list)
    guidance_topics_covered = Column(ARRAY(Text), default=list)
    immunizations_addressed = Column(String(10), default="false")
    screening_tools_used = Column(ARRAY(Text), default=list)
```

**Step 2: Commit**

```bash
git add src/db_models.py
git commit -m "FEATURE: Add well-child columns to CaseSession database model"
```

---

## Task 10: Update Frontend Types and API Client

**Files:**
- Modify: `web/src/types/case.ts`
- Modify: `web/src/api/client.ts`

**Step 1: Update TypeScript types**

In `web/src/types/case.ts`, add:

```typescript
export type VisitType = 'sick' | 'well_child';

export type WellChildPhase = 'growth_review' | 'developmental_screening' |
  'anticipatory_guidance' | 'immunizations' | 'parent_questions';

export interface CaseState {
  session_id: string;
  phase: string;
  patient: GeneratedPatient;
  visit_type?: VisitType;
  // ... existing fields ...
  // Well-child tracking
  growth_reviewed?: boolean;
  milestones_assessed?: string[];
  guidance_topics_covered?: string[];
  immunizations_addressed?: boolean;
  screening_tools_used?: string[];
  parent_concerns_addressed?: string[];
}

export interface GeneratedPatient {
  // ... existing fields ...
  chief_complaint?: string;  // Optional for well-child
  visit_age_months?: number;
  growth_data?: Record<string, unknown>;
  milestones?: Record<string, string[]>;
}

export interface StartCaseRequest {
  learner_level: string;
  condition_key?: string;
  time_constraint?: number;
  visit_type?: VisitType;
  visit_age_months?: number;
}

export interface WellChildDomainScore {
  score: number;
  feedback: string;
}

export interface WellChildScores {
  growth_interpretation: WellChildDomainScore;
  milestone_assessment: WellChildDomainScore;
  exam_thoroughness: WellChildDomainScore;
  anticipatory_guidance: WellChildDomainScore;
  immunization_knowledge: WellChildDomainScore;
  communication_skill: WellChildDomainScore;
}
```

**Step 2: Update API client types**

In `web/src/api/client.ts`, update:

```typescript
export interface BackendStartCaseRequest {
  learner_level: LearnerLevel;
  condition_key?: string;
  time_constraint?: number;
  visit_type?: 'sick' | 'well_child';
  visit_age_months?: number;
}

export interface BackendCaseState {
  // ... existing fields ...
  visit_type?: string;
  growth_reviewed?: boolean;
  milestones_assessed?: string[];
  guidance_topics_covered?: string[];
}

export interface DebriefData {
  // ... existing fields ...
  well_child_scores?: {
    growth_interpretation: { score: number; feedback: string };
    milestone_assessment: { score: number; feedback: string };
    exam_thoroughness: { score: number; feedback: string };
    anticipatory_guidance: { score: number; feedback: string };
    immunization_knowledge: { score: number; feedback: string };
    communication_skill: { score: number; feedback: string };
  };
}
```

**Step 3: Commit**

```bash
cd /Users/dochobbs/Downloads/Consult/MedEd/echo/web
git add src/types/case.ts src/api/client.ts
git commit -m "FEATURE: Add well-child TypeScript types and API client updates"
```

---

## Task 11: Update Frontend — Home Page

**Files:**
- Modify: `web/src/pages/Home.tsx`
- Modify: `web/src/hooks/useCase.tsx`

**Step 1: Update useCase hook to accept visit type**

In `web/src/hooks/useCase.tsx`, update `startCase` signature and API call:

```typescript
const startCase = useCallback(async (options?: {
  level?: LearnerLevel;
  condition?: string;
  visitType?: 'sick' | 'well_child';
  visitAgeMonths?: number;
}) => {
  // ...
  const response = await api.startCase({
    learner_level: options?.level || 'student',
    condition_key: options?.condition,
    visit_type: options?.visitType,
    visit_age_months: options?.visitAgeMonths,
  });
  // ...
}, []);
```

**Step 2: Update Home.tsx with visit type selector**

Add visit type toggle and well-child age picker. The page should show:
1. Learner level selector (existing)
2. Visit type toggle: "Sick Visit" | "Well-Child Visit"
3. If well-child selected: age picker with 13 visit ages
4. Start button

Key UX:
- Well-child ages show as cards: "Newborn", "2 Months", etc.
- Each card has a subtitle: "First vaccines, maternal depression screen"
- Selected age highlighted
- Start button says "Start Well-Child Visit" when well-child selected

**Step 3: Commit**

```bash
cd /Users/dochobbs/Downloads/Consult/MedEd/echo/web
git add src/pages/Home.tsx src/hooks/useCase.tsx
git commit -m "FEATURE: Add well-child visit type selector and age picker to Home page"
```

---

## Task 12: Update Frontend — Case Page Phase Indicator

**Files:**
- Modify: `web/src/pages/Case.tsx`

**Step 1: Add well-child phase labels**

Update the phase indicator to show well-child phases when `visit_type === 'well_child'`:

```typescript
const WELL_CHILD_PHASES = [
  { key: 'intro', label: 'Start' },
  { key: 'growth_review', label: 'Growth' },
  { key: 'developmental_screening', label: 'Development' },
  { key: 'exam', label: 'Exam' },
  { key: 'anticipatory_guidance', label: 'Guidance' },
  { key: 'immunizations', label: 'Vaccines' },
  { key: 'parent_questions', label: 'Wrap-Up' },
  { key: 'debrief', label: 'Debrief' },
];

const SICK_PHASES = [
  { key: 'intro', label: 'Start' },
  { key: 'history', label: 'History' },
  { key: 'exam', label: 'Exam' },
  { key: 'assessment', label: 'Assessment' },
  { key: 'plan', label: 'Plan' },
  { key: 'debrief', label: 'Debrief' },
];
```

Use `caseState?.visit_type === 'well_child'` to select which phase list to render.

**Step 2: Commit**

```bash
cd /Users/dochobbs/Downloads/Consult/MedEd/echo/web
git add src/pages/Case.tsx
git commit -m "FEATURE: Add well-child phase indicator to Case page"
```

---

## Task 13: Update Frontend — Debrief Card

**Files:**
- Modify: `web/src/components/DebriefCard.tsx`

**Step 1: Add domain score display for well-child debriefs**

When `debrief.well_child_scores` is present, render a domain score grid:
- 6 domains in a 2x3 or 3x2 grid
- Each shows: domain name, score (0-10), feedback text
- Color coded: green (8-10), yellow (5-7), red (0-4)
- Total score shown as average

When `well_child_scores` is absent (sick visit), existing debrief display unchanged.

**Step 2: Commit**

```bash
cd /Users/dochobbs/Downloads/Consult/MedEd/echo/web
git add src/components/DebriefCard.tsx
git commit -m "FEATURE: Add well-child domain scores to debrief display"
```

---

## Task 14: Build Frontend and Integration Test

**Step 1: Build the frontend**

Run: `cd /Users/dochobbs/Downloads/Consult/MedEd/echo/web && npm run build`
Expected: Build succeeds with no TypeScript errors

**Step 2: Run backend tests**

Run: `cd /Users/dochobbs/Downloads/Consult/MedEd/echo && python -m pytest tests/ -v`
Expected: All tests pass

**Step 3: Start the server and verify**

Run: `cd /Users/dochobbs/Downloads/Consult/MedEd/echo && source .venv/bin/activate && uvicorn src.main:app --port 8001 &`

Verify endpoints:
- `GET /case/frameworks?type=well_child` returns 13 frameworks
- `GET /case/frameworks?type=sick` returns sick-visit frameworks
- `GET /case/frameworks` returns all frameworks
- `GET /health` returns healthy

**Step 4: Commit build output**

```bash
git add web/dist/
git commit -m "FEATURE: Build frontend with well-child visit support"
```

---

## Task 15: Final Commit and Cleanup

**Step 1: Run all tests one final time**

Run: `cd /Users/dochobbs/Downloads/Consult/MedEd/echo && python -m pytest tests/ -v`
Expected: All tests pass

**Step 2: Final commit with any remaining changes**

```bash
git add -A
git status  # Review — make sure nothing unexpected
git commit -m "FEATURE: Well-child visit support — complete implementation"
```

---

## Summary

| Task | Description | Files Changed |
|------|-------------|---------------|
| 1 | Extend case models | `models.py`, `test_models.py` |
| 2 | Schema + first 3 frameworks | 4 YAML files |
| 3 | Remaining 10 frameworks | 10 YAML files |
| 4 | Update framework loader | `loader.py`, `test_framework_loader.py` |
| 5 | Well-child generator | `well_child_generator.py`, test |
| 6 | Tutor prompts | `well_child.md`, `well_child_debrief.md` |
| 7 | Update tutor logic | `tutor.py` |
| 8 | Update case router | `router.py` |
| 9 | Update DB models | `db_models.py` |
| 10 | Frontend types + API | `case.ts`, `client.ts` |
| 11 | Home page UI | `Home.tsx`, `useCase.tsx` |
| 12 | Case page phases | `Case.tsx` |
| 13 | Debrief card | `DebriefCard.tsx` |
| 14 | Build + integration test | Build output |
| 15 | Final cleanup | Any remaining |

**Total new files:** 17 (13 frameworks, 2 prompts, 1 generator, 1 test)
**Total modified files:** 11
**Estimated commits:** 15
