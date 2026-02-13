# Well-Child Visit Support — Design Document

**Date:** 2026-02-12
**Status:** Approved
**Scope:** Major feature — adds pediatric well-child checks as a first-class case type

## Problem

Echo currently only supports sick visits (complaint-driven encounters). Well-child
visits are a fundamentally different type of learner-patient-attending interaction —
age-driven, preventive, and focused on comprehensive care rather than diagnosis.
Residents spend significant time doing well-child visits and need to practice the
complete workflow: growth review, developmental screening, anticipatory guidance,
immunizations, and handling incidental findings.

## Design Overview

Add `well_child` as a new visit type alongside the existing `sick` visit type.
Well-child cases use a different phase flow, different teaching frameworks (organized
by visit age rather than condition), and different debrief scoring (completeness
across preventive care domains rather than diagnostic accuracy).

Everything is additive — existing sick visit cases work exactly as before.

---

## 1. Visit Type Architecture

### Sick Visit Flow (existing, unchanged)
```
intro → history → exam → assessment → plan → debrief → complete
```

### Well-Child Visit Flow (new)
```
intro → growth_review → developmental_screening → exam →
anticipatory_guidance → immunizations → parent_questions → debrief → complete
```

### Phase Descriptions

| Phase | Purpose | Teaching Focus |
|-------|---------|---------------|
| **Intro** | Present the scenario — visit age, parent, any stated concerns | Setting the stage |
| **Growth Review** | Weight, length, HC with percentiles and trajectory | Interpret trends, not just numbers |
| **Developmental Screening** | Age-appropriate milestones, screening tools | Know tools (ASQ-3, M-CHAT-R/F) and when to use them |
| **Exam** | Head-to-toe with age-specific focus | Age-appropriate exam priorities, detecting incidental findings |
| **Anticipatory Guidance** | Safety, nutrition, sleep, development counseling | Core preventive pediatrics skill — parent-centered communication |
| **Immunizations** | What's due, catch-up, counseling | Vaccine knowledge + communication skill with hesitant parents |
| **Parent Questions** | "Doorknob moment" — parent raises a new concern | Pivot from preventive to diagnostic thinking |
| **Debrief** | Structured review across all domains | Completeness and accuracy of preventive care |

---

## 2. Well-Child Framework Schema

Each well-child framework is organized by **visit age** (not condition). Located at
`knowledge/frameworks/well_child_*.yaml`.

### Schema: `_well_child_schema.yaml`

```yaml
# Required fields
topic: str                    # "2 Month Well-Child Visit"
visit_type: "well_child"      # Always "well_child"
visit_age_months: int         # Age in months (0 for newborn)
category: "well_child"        # Always "well_child"

teaching_goals:               # 4-6 learning objectives for this visit age
  - str

expected_milestones:          # CDC 2022 milestones (75th percentile standard)
  gross_motor: [str]
  fine_motor: [str]
  language: [str]
  social_emotional: [str]
  cognitive: [str]

screening_tools:              # Recommended screenings at this age
  - tool: str                 # e.g., "ASQ-3", "M-CHAT-R/F", "EPDS"
    when: str                 # "routine" or "if concern"

anticipatory_guidance:        # Bright Futures 4th edition topics
  safety: [str]
  nutrition: [str]
  development: [str]
  behavior: [str]
  sleep: [str]                # Optional, not all ages have specific sleep guidance

immunizations_due:            # Per 2025 CDC/ACIP schedule
  - vaccine: str
    cvx: int
    dose_number: str          # "1st dose", "2nd dose", etc.
    notes: str                # Optional, e.g., "RV5 only; RV1 is 2-dose series"

physical_exam_focus:          # Age-specific exam priorities
  - area: str                 # e.g., "hips"
    detail: str               # "Barlow and Ortolani maneuvers for DDH"
    teaching_point: str       # Why this matters at this age

common_mistakes:              # Typical learner errors at this visit age
  - str

possible_findings:            # Incidental findings that can surface
  - finding: str              # Key identifier
    description: str          # What the finding looks like
    probability: float        # 0.0-1.0, likelihood of rolling this finding
    framework_link: str       # Links to sick-visit framework for clinical depth
    age_relevance: str        # Why this finding matters at this age

parent_styles:                # Realistic parent presentations
  - str

sources:                      # Clinical references
  - str
```

### Framework Files (13 total)

| File | Visit Age | Key Teaching Highlights |
|------|-----------|----------------------|
| `well_child_newborn.yaml` | 0 (birth) | Newborn screen, CCHD, jaundice, hip exam, safe sleep, feeding |
| `well_child_2mo.yaml` | 2 months | First big vaccine visit, maternal depression screen, tummy time |
| `well_child_4mo.yaml` | 4 months | Strabismus resolution, rolling readiness, intro solids discussion |
| `well_child_6mo.yaml` | 6 months | Complementary foods, fluoride, oral health, allergenic food intro |
| `well_child_9mo.yaml` | 9 months | ASQ-3 screening, stranger anxiety, finger foods, childproofing |
| `well_child_12mo.yaml` | 12 months | MMR/varicella/HepA, bottle weaning, walking assessment, lead/anemia |
| `well_child_15mo.yaml` | 15 months | Walking milestone (CDC 2022 update), limit-setting, tantrums |
| `well_child_18mo.yaml` | 18 months | M-CHAT-R/F autism screen, ASQ-3, language explosion, screen time |
| `well_child_24mo.yaml` | 24 months | M-CHAT follow-up, toilet readiness, BMI start, CDC growth charts |
| `well_child_3yr.yaml` | 3 years | BP screening starts, vision screening, preschool readiness |
| `well_child_4yr.yaml` | 4 years | Pre-K vaccines (DTaP #5, IPV #4, MMR #2, Var #2), school readiness |
| `well_child_5yr.yaml` | 5 years | Kindergarten entry, catch-up vaccines, audiometry, independence |
| `well_child_adolescent.yaml` | 11-17 years | Tdap, HPV, MenACWY, HEEADSSS, depression/substance screening |

---

## 3. Immunization Reference Data

All immunization data sourced from 2025 CDC/ACIP recommended schedule.

### CVX Code Reference

| Vaccine | CVX | Notes |
|---------|-----|-------|
| Hepatitis B (pediatric) | 08 | Birth, 1-2mo, 6-18mo |
| Rotavirus RV1 (Rotarix) | 119 | 2-dose series: 2mo, 4mo |
| Rotavirus RV5 (RotaTeq) | 116 | 3-dose series: 2mo, 4mo, 6mo |
| DTaP | 20 | 5-dose: 2, 4, 6, 15-18mo, 4-6yr |
| Hib (PRP-T) | 48 | 4-dose: 2, 4, 6, 12-15mo |
| Hib (PRP-OMP) | 49 | 3-dose: 2, 4, 12-15mo (no 6mo dose) |
| PCV20 (Prevnar 20) | 216 | 4-dose: 2, 4, 6, 12-15mo |
| PCV15 (Vaxneuvance) | 215 | 4-dose: 2, 4, 6, 12-15mo (alternative) |
| IPV | 10 | 4-dose: 2, 4, 6-18mo, 4-6yr |
| Influenza (IIV) | 150 | Annual from 6mo; 2 doses first season |
| MMR | 03 | 2-dose: 12-15mo, 4-6yr |
| Varicella | 21 | 2-dose: 12-15mo, 4-6yr |
| Hepatitis A (pediatric) | 83 | 2-dose: 12-23mo, 6+ months later |
| Tdap | 115 | 1 dose at 11-12yr |
| HPV 9-valent | 165 | 2-dose if started <15yr; 3-dose if >=15yr |
| MenACWY | 114/136/203 | 2-dose: 11-12yr, 16yr booster |
| MenB | 162/163 | Shared clinical decision: 16-18yr preferred |
| MenABCWY (Penbraya) | 316 | Combined MenACWY+MenB option, 10-25yr |
| Nirsevimab (RSV mAb) | 306/307 | All infants <8mo in RSV season; not a vaccine |

### Key Clinical Notes
- **PCV20 vs PCV15:** PCV20 provides broader serotype coverage (20 vs 15). Both are
  acceptable per 2025 ACIP. PCV13 is being phased out. If PCV15 used for primary series,
  supplemental PCV20 is NOT needed for healthy children.
- **Hib dosing:** PRP-OMP (PedvaxHIB) = 3 doses (no 6mo). PRP-T (ActHIB) = 4 doses.
- **Rotavirus window:** First dose before 15 weeks 0 days; complete by 8 months 0 days.
- **HPV:** 2-dose series if started before 15th birthday (0, 6-12mo). 3-dose if >=15yr.
- **Nirsevimab:** Monoclonal antibody, not vaccine. <5kg = 50mg (0.5mL, CVX 306),
  >=5kg = 100mg (1.0mL, CVX 307). Given at birth hospitalization if Oct-Mar.

---

## 4. Developmental Milestones Reference

All milestones per CDC "Learn the Signs. Act Early." (2022 update, 75th percentile).

### Key 2022 Changes
- Walking alone: moved from 12mo to **15mo**
- Rolling: moved from 4mo to **6mo**
- Crawling: **removed** as a milestone (some children skip it)
- New milestone check ages added: **15 months** and **30 months**

### Milestones by Visit Age

**Newborn:** Reflexes (Moro, rooting, sucking, grasp), flexor tone, alertness, cry

**2 months:** Social smile, coos, lifts head on tummy, opens hands, watches faces

**4 months:** Laughs, coos "oooo/aahh", holds head steady, brings hands to mouth,
pushes up on elbows, holds toy placed in hand

**6 months:** Knows familiar people, laughs, blows raspberries, rolls tummy to back,
reaches for toys, leans on hands when sitting

**9 months:** Stranger anxiety, "mamama/bababa", object permanence emerging, sits
without support, rakes food, transfers objects hand to hand

**12 months:** Waves bye-bye, "mama/dada" with meaning, understands "no", pincer
grasp, pulls to stand, cruises furniture

**15 months:** Points to ask, tries 1-2 words beyond mama/dada, stacks 2 blocks,
takes a few steps independently, feeds self with fingers

**18 months:** 3+ words, follows 1-step directions without gestures, walks without
holding on, scribbles, drinks from open cup, climbs on/off furniture

**24 months:** 2-word combinations, points to body parts, kicks ball, runs,
uses spoon, 50+ word vocabulary

**3 years:** Conversations (2+ exchanges), asks who/what/where/why, draws circle,
dresses self partially, uses fork, plays with other children

**4 years:** 4+ word sentences, pretend play, draws person (3+ body parts), catches
large ball, holds crayon with fingers (not fist)

**5 years:** Tells stories, counts to 10, writes some letters, hops on one foot,
buttons some buttons, 5-10 minute attention span

**Adolescent:** Tanner staging, abstract thinking, identity formation, emotional
regulation, risk assessment (no formal CDC milestone checklist)

---

## 5. Screening Schedule Reference

Per AAP Bright Futures Periodicity Schedule (updated Feb 2025).

| Screening | Ages |
|-----------|------|
| Newborn metabolic screen | Birth (after 24hr) |
| CCHD pulse oximetry | Birth (after 24hr); single retest on fail (2025 update) |
| Hearing (newborn) | Birth (OAE or ABR) |
| Bilirubin | Before discharge |
| Maternal depression (EPDS/PHQ) | 1, 2, 4, 6 months |
| Developmental (ASQ-3) | 9, 18, 30 months |
| Autism (M-CHAT-R/F) | 18, 24 months |
| Anemia (Hgb/Hct) | 9-12 months |
| Lead | 12mo (risk), 24mo (risk); required for Medicaid at both |
| Oral health / fluoride varnish | Every 6mo from first tooth through age 5 |
| Blood pressure | Annually from age 3 |
| Vision | 3-5yr (instrument or Snellen); 11-14, 15-17, 18-21yr |
| Hearing (audiometry) | 4yr, 5yr; 11-14, 15-17, 18-21yr |
| BMI | From age 2, annually |
| Depression (PHQ-A) | Annually from age 12 |
| Anxiety | Per clinical judgment |
| Substance use (CRAFFT 2.1) | Annually from age 12 |
| Lipid screening | Once 9-11yr; repeat 17-21yr |
| Scoliosis | Girls 10-12, boys 13-14 |
| STI screening | Sexually active adolescents |
| HEEADSSS 3.0 | Every adolescent visit |

### Growth Charts
- **0-24 months:** WHO growth charts
- **>= 2 years:** CDC growth charts
- **BMI-for-age:** Begins at 24 months on CDC charts

---

## 6. Data Model Changes

### New Enums

```python
class VisitType(str, Enum):
  SICK = "sick"
  WELL_CHILD = "well_child"
```

### CasePhase — Extended

```python
class CasePhase(str, Enum):
  # Shared phases
  INTRO = "intro"
  EXAM = "exam"
  DEBRIEF = "debrief"
  COMPLETE = "complete"

  # Sick visit phases (existing)
  HISTORY = "history"
  ASSESSMENT = "assessment"
  PLAN = "plan"

  # Well-child phases (new)
  GROWTH_REVIEW = "growth_review"
  DEVELOPMENTAL_SCREENING = "developmental_screening"
  ANTICIPATORY_GUIDANCE = "anticipatory_guidance"
  IMMUNIZATIONS = "immunizations"
  PARENT_QUESTIONS = "parent_questions"
```

### GeneratedPatient — Extended

```python
class GeneratedPatient(BaseModel):
  # Existing fields (unchanged)
  id: str
  name: str
  age: int
  age_unit: str = "months"
  sex: str
  weight_kg: float
  parent_name: str
  parent_style: str
  condition_key: str
  condition_display: str
  symptoms: list[str]
  vitals: dict[str, float]
  exam_findings: list[dict]

  # Modified: now optional (well-child has no chief complaint)
  chief_complaint: Optional[str] = None

  # New: well-child specific fields
  visit_age_months: Optional[int] = None
  growth_data: Optional[dict] = None        # {weight_pct, length_pct, hc_pct, trajectory}
  milestones: Optional[dict] = None         # {gross_motor: [...], fine_motor: [...], ...}
  immunization_history: Optional[list] = None  # Previously received vaccines
  incidental_finding: Optional[dict] = None    # Rolled finding, if any
```

### CaseState — Extended

```python
class CaseState(BaseModel):
  # Existing fields (unchanged)
  session_id: str
  phase: CasePhase
  patient: GeneratedPatient
  learner_level: LearnerLevel
  history_gathered: list[str]
  exam_performed: list[str]
  differential: list[str]
  plan_proposed: list[str]
  hints_given: int
  teaching_moments: list[str]
  started_at: datetime
  time_constraint: Optional[int]
  conversation: list[dict]

  # New fields
  visit_type: VisitType = VisitType.SICK

  # Well-child tracking
  growth_reviewed: bool = False
  milestones_assessed: list[str] = Field(default_factory=list)
  guidance_topics_covered: list[str] = Field(default_factory=list)
  immunizations_addressed: bool = False
  screening_tools_used: list[str] = Field(default_factory=list)
  parent_concerns_addressed: list[str] = Field(default_factory=list)
```

### StartCaseRequest — Extended

```python
class StartCaseRequest(BaseModel):
  # Existing fields (unchanged)
  learner_level: LearnerLevel = LearnerLevel.STUDENT
  condition_key: Optional[str] = None
  time_constraint: Optional[int] = None
  severity: Optional[CaseSeverity] = None
  age_bracket: Optional[AgeBracket] = None
  presentation: Optional[CasePresentation] = None
  complexity: Optional[CaseComplexity] = None

  # New fields
  visit_type: VisitType = VisitType.SICK
  visit_age_months: Optional[int] = None  # Required when visit_type == "well_child"
```

### DebriefData — Extended

```python
class DebriefData(BaseModel):
  # Existing fields (unchanged)
  summary: str
  strengths: list[str]
  areas_for_improvement: list[str]
  missed_items: list[str]
  teaching_points: list[str]
  follow_up_resources: list[str]

  # New: well-child domain scores (None for sick visits)
  well_child_scores: Optional[dict] = None
  # {
  #   "growth_interpretation": {"score": 0-10, "feedback": str},
  #   "milestone_assessment": {"score": 0-10, "feedback": str},
  #   "exam_thoroughness": {"score": 0-10, "feedback": str},
  #   "anticipatory_guidance": {"score": 0-10, "feedback": str},
  #   "immunization_knowledge": {"score": 0-10, "feedback": str},
  #   "communication_skill": {"score": 0-10, "feedback": str},
  # }
```

---

## 7. Tutor Prompt Architecture

### File Structure

```
src/prompts/
├── system.md              # Existing — core Socratic pedagogy (unchanged)
├── feedback.md            # Existing (unchanged)
├── question.md            # Existing (unchanged)
├── debrief.md             # Existing (unchanged)
├── well_child.md          # NEW — well-child teaching mode prompt
└── well_child_debrief.md  # NEW — well-child debrief scoring prompt
```

### well_child.md — Teaching Prompt

Core principles:
- **No single right answer** — assess comprehensive preventive care, not diagnosis
- **Don't prompt the learner** — see what they remember to cover on their own
- **Play the parent realistically** — questions, pushback, misconceptions, grandparent advice
- **Phase-specific teaching** — different Socratic approach per phase
- **Incidental findings** — if rolled, test the pivot from preventive to diagnostic thinking

Phase-specific guidance:
- **Growth Review:** Don't accept "looks fine" — push for trajectory interpretation
- **Developmental Screening:** Present milestones through parent report; see if learner
  asks about all domains and knows which tools apply
- **Exam:** Present findings conversationally; include incidental finding if rolled
- **Anticipatory Guidance:** Play parent with realistic questions and misconceptions;
  see what topics the learner covers without prompting
- **Immunizations:** State what's due; if parent hesitant, play it realistically
- **Parent Questions:** Natural "doorknob moment" — test adaptability

### well_child_debrief.md — Scoring Prompt

Six domains scored 0-10:
1. **Growth Interpretation** — Did they analyze trajectory, not just read numbers?
2. **Milestone Assessment** — Did they cover all domains? Use correct screening tools?
3. **Exam Thoroughness** — Age-appropriate focused exam? Caught incidental finding?
4. **Anticipatory Guidance** — Covered safety, nutrition, sleep, development? Accurate?
5. **Immunization Knowledge** — Knew what was due? Counseled effectively?
6. **Communication Skill** — Parent-centered? Warm? Handled concerns well?

### Tutor.py Changes

Methods affected:
- `_build_case_system_prompt()` — branches on `visit_type` to load well-child prompt +
  age-specific framework instead of sick-visit condition data
- `_update_case_phase()` — parallel phase detection path for well-child phases
- `generate_case_opening()` — different opening narrative for well-child (no chief complaint)
- `generate_debrief()` — well-child debrief uses domain scoring instead of diagnostic accuracy
- `_detect_stuck()` — adapts stuck detection for well-child context

---

## 8. Generator Changes

### New: `src/cases/well_child_generator.py`

Generates healthy patients at specified visit ages:
- Realistic growth data (weight, length, HC with percentiles and trajectory)
- Age-appropriate milestone status (most met, some variable)
- Immunization history (up to date or with realistic gaps)
- Parent personality from framework `parent_styles`
- Rolls `possible_findings` using probability weights
- If finding rolled: links to sick-visit framework for clinical depth

### Dynamic Generator Extension

`src/cases/dynamic_generator.py` gains a `generate_well_child_case()` method:
- Takes `visit_age_months` and `learner_level`
- Loads the well-child framework for that age
- Uses Claude to generate a unique patient while maintaining framework teaching goals
- Returns `CaseState` with `visit_type: "well_child"`

---

## 9. API Changes

### Modified Endpoints

**`POST /case/start/dynamic`** — No signature change. Reads `visit_type` from
`StartCaseRequest` and routes to well-child generator when `visit_type == "well_child"`.

**`POST /case/message`** — No change. Tutor reads `visit_type` from `case_state`.

**`POST /case/debrief`** — No change. Tutor generates appropriate debrief based on
`visit_type`.

**`GET /case/frameworks`** — Adds optional `type` query parameter:
- `/case/frameworks` — all frameworks (backward compatible)
- `/case/frameworks?type=sick` — sick-visit only
- `/case/frameworks?type=well_child` — well-child only

### No New Endpoints

The existing case lifecycle endpoints handle both visit types.

---

## 10. Frontend Changes

### Home Page (`web/src/pages/Home.tsx`)

Add visit type selector before case configuration:
- **Sick Visit** → existing condition picker (unchanged)
- **Well-Child Visit** → age picker with 13 visit ages
  - Each shows: age label, key teaching highlight
  - Example: "2 Months — First vaccines, maternal depression screen"
  - Example: "18 Months — Autism screening (M-CHAT-R/F)"

### Case Page (`web/src/pages/Case.tsx`)

- Phase indicator shows well-child phases when `visit_type == "well_child"`
- Phase labels: "Growth Review", "Development", "Exam", "Guidance", "Vaccines", "Wrap-Up"
- Conversation interface unchanged (still message-based chat)

### Case Hook (`web/src/hooks/useCase.tsx`)

- Passes `visit_type` and `visit_age_months` in start request
- Handles `well_child_scores` in debrief response for domain-based display

### Debrief Display (`web/src/components/DebriefCard.tsx`)

- When `well_child_scores` present: shows radar/bar chart of 6 domain scores
- When absent (sick visit): existing debrief display unchanged

### Widget (`widget/`)

- `EchoWidget` accepts optional `visitType` and `visitAgeMonths` props
- Default remains `sick` for backward compatibility

---

## 11. File Inventory

### New Files
```
knowledge/frameworks/_well_child_schema.yaml
knowledge/frameworks/well_child_newborn.yaml
knowledge/frameworks/well_child_2mo.yaml
knowledge/frameworks/well_child_4mo.yaml
knowledge/frameworks/well_child_6mo.yaml
knowledge/frameworks/well_child_9mo.yaml
knowledge/frameworks/well_child_12mo.yaml
knowledge/frameworks/well_child_15mo.yaml
knowledge/frameworks/well_child_18mo.yaml
knowledge/frameworks/well_child_24mo.yaml
knowledge/frameworks/well_child_3yr.yaml
knowledge/frameworks/well_child_4yr.yaml
knowledge/frameworks/well_child_5yr.yaml
knowledge/frameworks/well_child_adolescent.yaml
src/prompts/well_child.md
src/prompts/well_child_debrief.md
src/cases/well_child_generator.py
```

### Modified Files
```
src/cases/models.py              — Add VisitType, new phases, extended models
src/cases/router.py              — Route well-child cases, add framework filter
src/cases/dynamic_generator.py   — Add generate_well_child_case()
src/core/tutor.py                — Branch on visit_type for prompts and phase logic
src/frameworks/loader.py         — Load well-child frameworks by visit age
src/db_models.py                 — Add visit_type column to CaseSession
web/src/pages/Home.tsx           — Visit type selector + age picker
web/src/pages/Case.tsx           — Well-child phase indicator
web/src/hooks/useCase.tsx        — Pass visit_type in requests
web/src/components/DebriefCard.tsx — Domain score display
web/src/types/case.ts            — TypeScript types for new fields
widget/src/types.ts              — Add visitType prop
```

---

## 12. Implementation Order

### Phase 1: Data Foundation
1. Create `_well_child_schema.yaml`
2. Create all 13 well-child framework YAML files (verified clinical data)
3. Update `models.py` with new enums and extended models
4. Update `db_models.py` with visit_type column

### Phase 2: Generator
5. Create `well_child_generator.py`
6. Extend `dynamic_generator.py` with `generate_well_child_case()`
7. Update `loader.py` to handle well-child frameworks

### Phase 3: Tutor
8. Create `well_child.md` prompt
9. Create `well_child_debrief.md` prompt
10. Update `tutor.py` — system prompt branching, phase detection, debrief

### Phase 4: API
11. Update `router.py` — route well-child cases, framework filter
12. Test API end-to-end with well-child cases

### Phase 5: Frontend
13. Update Home page with visit type selector + age picker
14. Update Case page with well-child phase indicator
15. Update DebriefCard with domain scores
16. Update TypeScript types and hooks
17. Update widget types

### Phase 6: Testing & Polish
18. Test all 13 visit ages end-to-end
19. Verify clinical accuracy of framework content
20. Test incidental finding flow (well-child → sick-visit crossover)

---

## 13. Clinical Data Sources

All clinical data in this design was verified against:
- AAP Bright Futures Periodicity Schedule (updated February 2025, approved December 2024)
- CDC/ACIP 2025 Recommended Child and Adolescent Immunization Schedule
- CDC "Learn the Signs. Act Early." Developmental Milestones (2022 update)
- CDC CVX Vaccine Code database
- AAP CCHD Screening Update (January 2025)
- CDC RSV Immunization Guidance for Infants and Young Children
- Prevnar 20 (PCV20) Pediatric Dosing — Pfizer
