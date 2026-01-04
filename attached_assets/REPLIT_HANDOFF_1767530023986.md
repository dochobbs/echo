# Echo Teaching Frameworks - Replit Integration Guide

**Date:** January 3, 2026
**Summary:** 100 pediatric condition teaching frameworks for dynamic case generation

---

## What's Being Added

100 YAML teaching frameworks covering the full pediatric primary care curriculum. These lightweight files (~50-60 lines each) provide teaching guardrails for Echo's AI tutor to generate clinically accurate, educationally valuable cases.

### Framework Categories

| Category | Count | Key Conditions |
|----------|-------|----------------|
| Newborn/Infant | 15 | febrile_infant, hyperbilirubinemia, safe_sleep_sids, ddh, colic |
| Infectious Disease | 17 | otitis_media, croup, uti, strep_pharyngitis, meningitis |
| Respiratory/Allergy | 5 | asthma, bronchiolitis, pneumonia, anaphylaxis |
| Dermatology | 11 | atopic_dermatitis, acne, tinea, infantile_hemangiomas |
| Behavioral/Developmental | 12 | adhd, autism, depression, anxiety, eating_disorders |
| GI | 6 | constipation, appendicitis, gerd, celiac, intussusception |
| Emergency/Trauma | 10 | head_injury, febrile_seizures, kawasaki, burns, child_abuse |
| MSK | 6 | limping_child, jia, scoliosis, hsp, apophysitis |
| Endocrine | 7 | obesity, type2_diabetes, thyroid, puberty_disorders |
| Nephrology/Urology | 7 | uti, hypertension, enuresis, acute_scrotum |
| Hematology/Oncology | 2 | iron_deficiency_anemia, oncologic_emergencies |
| Adolescent/GYN | 3 | stis, contraception, dysmenorrhea |

---

## File Structure

```
knowledge/
└── frameworks/
    ├── _schema.yaml          # Schema documentation
    ├── otitis_media.yaml     # Example framework
    ├── febrile_infant.yaml
    ├── asthma.yaml
    └── ... (100 total frameworks)
```

---

## Framework Schema

Each YAML framework contains:

```yaml
# Condition Name - Teaching Framework
topic: "Condition Name"
aliases: ["alternative names", "abbreviations"]
category: respiratory | gi | derm | behavioral | etc.
age_range_months: [min, max]

teaching_goals:
  - "Key learning objective 1"
  - "Key learning objective 2"

common_mistakes:
  - "Error learners commonly make"

red_flags:
  - "Safety-critical finding requiring action"

clinical_pearls:
  - "High-yield teaching point"

key_history_questions:
  - "Important question to ask"

key_exam_findings:
  - "What to look for on exam"

treatment_principles:
  - "First-line treatment approach"

disposition_guidance:
  - "When to refer, admit, or discharge"

parent_styles: [anxious, skeptical, experienced]

sources:
  - "AAP Guidelines, etc."
```

---

## How to Use in Echo

### 1. Loading Frameworks

```python
import yaml
from pathlib import Path

def load_frameworks():
    """Load all teaching frameworks into memory."""
    frameworks = {}
    framework_dir = Path("knowledge/frameworks")

    for file in framework_dir.glob("*.yaml"):
        if file.name.startswith("_"):
            continue
        with open(file) as f:
            data = yaml.safe_load(f)
            key = file.stem  # e.g., "otitis_media"
            frameworks[key] = data

    return frameworks

FRAMEWORKS = load_frameworks()
```

### 2. Finding Framework by Condition

```python
def find_framework(condition_name: str) -> dict | None:
    """Find framework by topic name or alias."""
    condition_lower = condition_name.lower()

    for key, framework in FRAMEWORKS.items():
        # Check exact key match
        if key == condition_lower.replace(" ", "_"):
            return framework

        # Check topic name
        if framework.get("topic", "").lower() == condition_lower:
            return framework

        # Check aliases
        aliases = [a.lower() for a in framework.get("aliases", [])]
        if condition_lower in aliases:
            return framework

    return None
```

### 3. Using in Case Generation Prompt

```python
def build_case_prompt(condition_key: str, learner_level: str) -> str:
    """Build prompt for Claude to generate a case."""
    framework = FRAMEWORKS.get(condition_key)

    if not framework:
        return "Generate a general pediatric case."

    return f"""
Generate a pediatric case for teaching {framework['topic']}.

TEACHING GOALS (what learner should understand):
{yaml.dump(framework['teaching_goals'])}

COMMON MISTAKES TO ADDRESS:
{yaml.dump(framework['common_mistakes'])}

RED FLAGS (must be recognized):
{yaml.dump(framework['red_flags'])}

CLINICAL PEARLS (high-yield points):
{yaml.dump(framework['clinical_pearls'])}

KEY HISTORY QUESTIONS:
{yaml.dump(framework['key_history_questions'])}

KEY EXAM FINDINGS:
{yaml.dump(framework['key_exam_findings'])}

TREATMENT PRINCIPLES:
{yaml.dump(framework['treatment_principles'])}

LEARNER LEVEL: {learner_level}
AGE RANGE: {framework['age_range_months'][0]}-{framework['age_range_months'][1]} months

Generate a realistic patient presentation within this age range.
Include parent personality from: {framework.get('parent_styles', [])}
"""
```

### 4. Using in Feedback/Teaching

```python
def get_teaching_context(condition_key: str) -> dict:
    """Get teaching context for providing feedback."""
    framework = FRAMEWORKS.get(condition_key, {})

    return {
        "goals": framework.get("teaching_goals", []),
        "pearls": framework.get("clinical_pearls", []),
        "mistakes": framework.get("common_mistakes", []),
        "red_flags": framework.get("red_flags", []),
    }
```

---

## API Endpoints to Add/Update

### GET /frameworks
List all available frameworks.

```python
@app.get("/frameworks")
async def list_frameworks():
    return {
        "count": len(FRAMEWORKS),
        "frameworks": [
            {
                "key": k,
                "topic": v["topic"],
                "category": v["category"],
                "age_range": v["age_range_months"]
            }
            for k, v in FRAMEWORKS.items()
        ]
    }
```

### GET /frameworks/{key}
Get a specific framework.

```python
@app.get("/frameworks/{key}")
async def get_framework(key: str):
    framework = FRAMEWORKS.get(key)
    if not framework:
        raise HTTPException(404, "Framework not found")
    return framework
```

### GET /frameworks/category/{category}
Get frameworks by category.

```python
@app.get("/frameworks/category/{category}")
async def get_by_category(category: str):
    return {
        "category": category,
        "frameworks": [
            {"key": k, "topic": v["topic"]}
            for k, v in FRAMEWORKS.items()
            if v.get("category") == category
        ]
    }
```

---

## Case Generation Integration

When starting a case, the flow should be:

1. **User requests case** (specific condition or random)
2. **Load framework** for that condition
3. **Pass framework to Claude** as teaching context
4. **Generate case** within framework constraints
5. **Track teaching goals** during conversation
6. **Debrief** using framework pearls and common mistakes

### Example Case Start Request

```json
{
  "condition_key": "otitis_media",
  "learner_level": "student",
  "time_constraint": 15
}
```

### Example Case Start Response

```json
{
  "session_id": "abc123",
  "patient": {
    "name": "Maya Johnson",
    "age_months": 18,
    "chief_complaint": "My daughter has been pulling at her ear and had a fever last night"
  },
  "teaching_context": {
    "condition": "Acute Otitis Media",
    "goals": ["Distinguish AOM from OME", "Know watchful waiting criteria"],
    "red_flags": ["Mastoiditis signs", "Toxic appearance"]
  }
}
```

---

## Testing

After integration, test with:

```bash
# List all frameworks
curl http://localhost:8001/frameworks

# Get specific framework
curl http://localhost:8001/frameworks/otitis_media

# Start a case with framework
curl -X POST http://localhost:8001/case/start \
  -H "Content-Type: application/json" \
  -d '{"condition_key": "febrile_infant", "learner_level": "resident"}'
```

---

## Files Included

1. **This document** (`REPLIT_HANDOFF.md`)
2. **Framework schema** (`knowledge/frameworks/_schema.yaml`)
3. **100 condition frameworks** (`knowledge/frameworks/*.yaml`)
4. **Frameworks archive** (`frameworks.tar.gz`) - all YAML files bundled

---

## Questions?

These frameworks are designed to be:
- **Lightweight** - Quick to load, minimal memory
- **Flexible** - Claude uses them as guardrails, not rigid scripts
- **Extensible** - Easy to add new conditions
- **Clinically accurate** - Based on AAP/CDC guidelines

The key insight: We don't need to generate full condition definitions. Claude already knows medicine. These frameworks just tell it **what to teach** and **what mistakes to watch for**.
