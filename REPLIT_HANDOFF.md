# Echo Platform Update - Replit Integration Guide

**Date:** January 17, 2026
**Summary:** Major platform improvements - case variants, admin dashboard, debrief Q&A, C-CDA patient import

---

## What's New in This Update

### 1. Case Variant Parameters
Cases can now be customized with variant parameters for richer teaching scenarios.

**New parameters on `POST /case/start/dynamic`:**
```json
{
  "condition_key": "otitis_media",
  "learner_level": "student",
  "severity": "severe",
  "age_bracket": "infant",
  "presentation": "atypical",
  "complexity": "challenging"
}
```

| Parameter | Options |
|-----------|---------|
| `severity` | `mild`, `moderate`, `severe` |
| `age_bracket` | `neonate`, `infant`, `toddler`, `child`, `adolescent` |
| `presentation` | `typical`, `atypical`, `early`, `late` |
| `complexity` | `straightforward`, `nuanced`, `challenging` |

All parameters are optional - if not specified, Claude picks randomly.

---

### 2. Post-Debrief Q&A
Learners can now revisit debriefs and ask follow-up questions.

**New endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/case/{session_id}/debrief` | GET | Get structured debrief data |
| `/case/{session_id}/question` | POST | Ask follow-up questions |

**Example Q&A request:**
```json
POST /case/abc123/question
{
  "question": "Why was amoxicillin better than azithromycin here?",
  "previous_questions": []
}
```

---

### 3. Admin Dashboard
Platform administrators can view all users and cases.

**New endpoints (require `role: "admin"`):**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/users` | GET | List all users with stats |
| `/admin/users/{id}` | GET | User detail |
| `/admin/cases` | GET | List all cases (filterable) |
| `/admin/cases/{session_id}` | GET | Full case detail with transcript |
| `/admin/metrics` | GET | Platform-wide metrics |
| `/admin/metrics/struggles` | GET | Where learners struggle |

**Example metrics response:**
```json
{
  "total_users": 8,
  "active_last_7_days": 5,
  "total_cases": 47,
  "completed_cases": 41,
  "avg_case_duration_minutes": 12.3,
  "completion_rate": 0.87,
  "most_practiced_conditions": [
    {"condition": "Acute Otitis Media", "count": 12},
    {"condition": "Croup", "count": 8}
  ]
}
```

---

### 4. C-CDA Patient Import
Learners can import synthetic patient panels from C-CDA files (e.g., from Oread).

**New endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/patients/import` | POST | Upload C-CDA XML file |
| `/patients` | GET | List imported patients |
| `/patients/{id}` | GET | Get patient detail |
| `/patients/{id}` | DELETE | Remove patient from panel |

**What gets extracted from C-CDA:**
- Demographics (name, DOB, sex)
- Problem list (SNOMED/ICD-10 codes)
- Medication list (RxNorm codes)
- Allergy list
- Recent encounters

---

### 5. Describe-a-Case (Disabled)
The describe-a-case feature has been disabled pending future development. Endpoints are commented out but code is preserved.

---

## Database Migration Required

Add the `role` column to the users table:

```sql
ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'learner';
```

To create an admin user:
```sql
UPDATE users SET role = 'admin' WHERE email = 'your-admin@email.com';
```

---

## New File Structure

```
src/
├── admin/
│   ├── __init__.py
│   └── router.py           # Admin endpoints
├── patients/
│   ├── __init__.py
│   ├── models.py           # ImportedPatient, Problem, etc.
│   ├── ccda_parser.py      # C-CDA XML parser
│   └── router.py           # Patient import endpoints
├── cases/
│   ├── dynamic_generator.py  # NEW: Dynamic case generation
│   ├── models.py           # Updated: variant enums, debrief models
│   └── router.py           # Updated: debrief endpoints, variants
├── core/
│   └── tutor.py            # Updated: post-debrief Q&A
├── auth/
│   ├── models.py           # Updated: role field
│   └── router.py           # Updated: role in registration
└── main.py                 # Updated: new routers
```

---

## Testing the New Features

### Test Case Variants
```bash
curl -X POST http://localhost:8001/case/start/dynamic \
  -H "Content-Type: application/json" \
  -d '{
    "condition_key": "febrile_infant",
    "learner_level": "resident",
    "severity": "severe",
    "age_bracket": "neonate"
  }'
```

### Test Debrief Retrieval
```bash
# Get debrief for a completed case
curl http://localhost:8001/case/{session_id}/debrief \
  -H "Authorization: Bearer {token}"

# Ask a follow-up question
curl -X POST http://localhost:8001/case/{session_id}/question \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{"question": "What if the patient had a penicillin allergy?"}'
```

### Test Admin Endpoints
```bash
# Get platform metrics (requires admin role)
curl http://localhost:8001/admin/metrics \
  -H "Authorization: Bearer {admin_token}"

# List all users
curl http://localhost:8001/admin/users \
  -H "Authorization: Bearer {admin_token}"
```

### Test Patient Import
```bash
# Import a C-CDA file
curl -X POST http://localhost:8001/patients/import \
  -H "Authorization: Bearer {token}" \
  -F "file=@patient.xml"

# List imported patients
curl http://localhost:8001/patients \
  -H "Authorization: Bearer {token}"
```

---

## Previous Features (Still Active)

### Teaching Frameworks
100 YAML teaching frameworks in `knowledge/frameworks/` covering the pediatric curriculum.

### Framework Endpoints
| Endpoint | Description |
|----------|-------------|
| `GET /case/frameworks` | List all frameworks |
| `GET /frameworks` | List frameworks (alternate) |
| `GET /frameworks/{key}` | Get specific framework |

### Case Endpoints
| Endpoint | Description |
|----------|-------------|
| `POST /case/start` | Start case (static generator) |
| `POST /case/start/dynamic` | Start case (Claude + frameworks) |
| `POST /case/message` | Send message in case |
| `POST /case/debrief` | Get debrief for case |
| `GET /case/history` | List completed cases |
| `GET /case/{session_id}` | Resume a case |

---

## Environment Variables

Required:
```bash
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://...  # For persistence
```

Optional:
```bash
ELEVEN_LABS_API_KEY=...  # For voice features
EXA_API_KEY=...          # For citation search
```

---

## Known Limitations

1. **Patient import is in-memory only** - Imported patients don't persist to database yet
2. **Debrief storage is basic** - Structured debrief fields (strengths, improvements) need better storage
3. **No UI for new features** - Admin dashboard, patient import, and debrief Q&A need frontend work

---

## Next Steps for Frontend

1. **Case Start UI** - Add variant selectors (severity, age bracket, etc.)
2. **Debrief History** - Allow viewing past debriefs with Q&A interface
3. **Admin Dashboard** - New page for platform metrics and user management
4. **Patient Panel** - UI for importing and selecting patients for cases
