# Echo: AI Attending Tutor for Pediatric Medical Education

**Version:** 1.0
**Last Updated:** January 2026
**License:** MIT

---

## Table of Contents

1. [What is Echo?](#what-is-echo)
2. [Why Echo Exists](#why-echo-exists)
3. [Key Features](#key-features)
4. [Architecture Overview](#architecture-overview)
5. [The Case System](#the-case-system)
6. [Teaching Frameworks](#teaching-frameworks)
7. [Conditions Covered](#conditions-covered)
8. [API Reference](#api-reference)
9. [Authentication & Roles](#authentication--roles)
10. [Database Schema](#database-schema)
11. [Configuration](#configuration)
12. [Getting Started](#getting-started)
13. [Deployment](#deployment)
14. [Contributing](#contributing)
15. [Roadmap](#roadmap)

---

## What is Echo?

Echo is an **AI-powered attending physician tutor** that teaches pediatric clinical reasoning through interactive, Socratic case-based learning. Named after the Greek nymph who repeated speech, Echo provides real-time feedback and guidance as learners work through simulated patient encounters.

### Core Concept

Instead of passive learning (reading textbooks, watching lectures), Echo creates **active clinical simulations** where medical students, residents, and NP students:

1. Receive a patient presentation (chief complaint, vitals, history)
2. Gather additional history through questioning
3. Perform a focused physical exam
4. Develop a differential diagnosis
5. Create an assessment and plan
6. Receive detailed feedback on their clinical reasoning

Echo acts like a supportive attending physician - asking Socratic questions, offering hints when stuck, and providing comprehensive debriefs after each case.

---

## Why Echo Exists

### The Problem

Medical education faces several challenges:

- **Limited clinical exposure** - Students need to see hundreds of cases to develop pattern recognition, but clinical rotations provide limited diversity
- **Variable teaching quality** - Feedback depends on which attending is supervising that day
- **Fear of mistakes** - Real patients mean real consequences; learners may hesitate to voice differential diagnoses
- **Inconsistent assessment** - Different preceptors evaluate the same performance differently

### Echo's Solution

- **Unlimited case variety** - 124 pediatric conditions with dynamic generation for unique presentations
- **Consistent Socratic teaching** - Claude provides patient, encouraging feedback every time
- **Safe practice environment** - Make mistakes and learn without patient harm
- **Structured assessment** - Standardized debriefs track strengths and areas for improvement
- **Adaptive difficulty** - Cases adjust to learner level (student vs. resident vs. NP)

---

## Key Features

### 1. Dynamic Case Generation

Every case is unique. Even the same condition presents differently each time:

```
Same condition (Otitis Media) → Different patients:
├── 14-month-old with fever and ear tugging (typical)
├── 8-month-old with irritability only (atypical)
├── 2-year-old with bilateral AOM and treatment failure
└── 6-month-old with first episode, anxious parent
```

**Variant Parameters:**
- **Severity:** mild, moderate, severe
- **Age Bracket:** neonate, infant, toddler, child, adolescent
- **Presentation:** typical, atypical, early, late
- **Complexity:** straightforward, nuanced, challenging

### 2. Socratic Teaching Method

Echo never just gives answers. It guides learners to discover:

```
Learner: "I think it's an ear infection. I'll prescribe amoxicillin."

Echo: "You're thinking about otitis media - good consideration given
the fever and fussiness. Before we jump to treatment, what specific
findings on your ear exam would confirm AOM versus otitis media with
effusion? This distinction matters for your antibiotic decision."
```

### 3. Stuck Detection & Hints

When learners stall, Echo notices and offers supportive guidance:

```
Echo: "I notice you've been focused on the respiratory exam. That's
thorough! Given this infant's fever and irritability, are there any
other systems that might be worth examining? Think about common
sources of fever in this age group."
```

### 4. Comprehensive Debriefs

After each case, learners receive structured feedback:

- **What you did well** - Reinforces good clinical habits
- **Areas for improvement** - Specific, actionable feedback
- **Missed items** - Key findings or questions that were skipped
- **Teaching points** - Clinical pearls relevant to the case
- **Follow-up resources** - Guidelines, articles, recommended reading

### 5. Post-Debrief Q&A

Cases don't end at the debrief. Learners can ask follow-up questions:

```
Learner: "What if this patient had a penicillin allergy?"

Echo: "Great question! For penicillin-allergic patients with AOM,
your options depend on the reaction type. For non-severe reactions
(rash only), cefdinir is appropriate - cephalosporins have <1%
cross-reactivity. For severe reactions (anaphylaxis), consider
azithromycin, though coverage for resistant S. pneumoniae is lower..."
```

### 6. Admin Dashboard

Platform administrators can monitor:

- **User engagement** - Active users, case completion rates
- **Learning patterns** - Which conditions are practiced most
- **Struggle points** - Where learners get stuck or need hints
- **Platform metrics** - Overall usage trends

### 7. Patient Import (C-CDA)

Import synthetic patient panels from C-CDA XML files:

- Demographics (name, DOB, sex)
- Problem list with SNOMED/ICD-10 codes
- Medication list with RxNorm codes
- Allergies and reactions
- Recent encounter history

This enables cases based on "panel patients" with realistic medical histories.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Echo                                 │
│                   FastAPI Application                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Auth      │  │   Cases     │  │   Admin     │         │
│  │   Router    │  │   Router    │  │   Router    │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
│  ┌──────┴────────────────┴────────────────┴──────┐         │
│  │                  Core Tutor                    │         │
│  │            (Claude AI Integration)             │         │
│  └──────────────────────┬────────────────────────┘         │
│                         │                                   │
│  ┌──────────────────────┴────────────────────────┐         │
│  │            Teaching Frameworks                 │         │
│  │         (124 YAML Condition Files)             │         │
│  └───────────────────────────────────────────────┘         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                     Data Layer                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ PostgreSQL  │  │  In-Memory  │  │    YAML     │         │
│  │  (Users,    │  │  (Patients, │  │ (Frameworks,│         │
│  │   Cases)    │  │   Sessions) │  │  Conditions)│         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology |
|-------|------------|
| **Framework** | FastAPI (Python 3.11+) |
| **AI/LLM** | Anthropic Claude (Sonnet) |
| **Database** | PostgreSQL + SQLAlchemy |
| **Authentication** | JWT (HS256) with bcrypt |
| **Voice (optional)** | Eleven Labs TTS, Deepgram STT |
| **Validation** | Pydantic v2 |

### Project Structure

```
echo/
├── src/
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Environment configuration
│   ├── database.py             # SQLAlchemy setup
│   ├── db_models.py            # ORM models (User, CaseSession, Message)
│   │
│   ├── auth/                   # Authentication system
│   │   ├── router.py           # /auth endpoints
│   │   ├── models.py           # User, Token models
│   │   └── deps.py             # Auth dependencies
│   │
│   ├── cases/                  # Case management
│   │   ├── router.py           # /case endpoints
│   │   ├── models.py           # CaseState, Patient models
│   │   ├── generator.py        # Static case generation
│   │   ├── dynamic_generator.py # Claude-powered generation
│   │   └── persistence.py      # Database persistence
│   │
│   ├── admin/                  # Admin dashboard
│   │   └── router.py           # /admin endpoints
│   │
│   ├── patients/               # Patient import
│   │   ├── router.py           # /patients endpoints
│   │   ├── models.py           # ImportedPatient model
│   │   └── ccda_parser.py      # C-CDA XML parser
│   │
│   ├── core/                   # Core AI logic
│   │   ├── tutor.py            # Claude integration
│   │   ├── voice_in.py         # Speech-to-text
│   │   └── voice_out.py        # Text-to-speech
│   │
│   ├── frameworks/             # Framework loading
│   │   ├── loader.py           # YAML loader
│   │   └── router.py           # /frameworks endpoints
│   │
│   └── prompts/                # Claude prompts
│       └── *.md                # System prompts
│
├── knowledge/
│   ├── conditions/             # Legacy condition definitions (11)
│   └── frameworks/             # Teaching frameworks (124)
│
├── tests/                      # Test suite
├── web/                        # Frontend (React)
├── docs/                       # Documentation
└── requirements.txt            # Python dependencies
```

---

## The Case System

### Case Lifecycle

```
START → INTRO → HISTORY → EXAM → ASSESSMENT → PLAN → DEBRIEF → COMPLETE
```

1. **START** - Learner initiates case, selects condition (or random)
2. **INTRO** - Echo presents patient, chief complaint, initial vitals
3. **HISTORY** - Learner asks questions, Echo responds as parent/patient
4. **EXAM** - Learner performs focused physical exam
5. **ASSESSMENT** - Learner develops differential diagnosis
6. **PLAN** - Learner proposes workup, treatment, disposition
7. **DEBRIEF** - Echo provides comprehensive feedback
8. **COMPLETE** - Case archived with learning materials

### Case State Tracking

Echo tracks everything the learner discovers:

```python
CaseState:
  session_id: "abc-123"
  patient: GeneratedPatient(...)
  phase: "history"

  # What learner has discovered
  history_gathered: ["fever x 3 days", "ear tugging", "poor sleep"]
  exam_performed: ["TM bulging right", "mild rhinorrhea"]
  differential: ["AOM", "OME", "viral URI"]
  plan_proposed: ["amoxicillin", "pain control", "return precautions"]

  # Teaching tracking
  hints_given: 1
  teaching_moments: ["Correctly identified observation criteria"]

  # Full conversation
  conversation: [Message(...), Message(...), ...]
```

### Generated Patient Model

Each case creates a unique patient:

```python
GeneratedPatient:
  id: "patient-uuid"
  name: "Olivia Martinez"
  age: 14
  age_unit: "months"
  sex: "female"
  weight_kg: 9.8

  chief_complaint: "Fever and fussiness for 2 days"
  parent_name: "Maria"
  parent_style: "anxious"  # Affects dialogue

  condition_key: "otitis_media"
  condition_display: "Acute Otitis Media"

  # Hidden until discovered
  symptoms: ["fever", "ear tugging", "decreased appetite", "rhinorrhea"]
  vitals: {"temp": 38.9, "hr": 142, "rr": 28}
  exam_findings: [
    {"system": "ear", "finding": "right TM bulging, erythematous"},
    {"system": "ear", "finding": "left TM normal"},
    ...
  ]
```

---

## Teaching Frameworks

Each condition has a comprehensive teaching framework that guides case generation and assessment.

### Framework Structure

```yaml
# knowledge/frameworks/otitis_media.yaml

topic: "Acute Otitis Media"
aliases: ["AOM", "ear infection", "otitis"]
category: infectious
age_range_months: [6, 36]

teaching_goals:
  - "Distinguish AOM from OME using pneumatic otoscopy findings"
  - "Apply AAP observation option criteria appropriately"
  - "Select correct antibiotic and dosing"
  - "Counsel on pain management as priority"
  - "Identify indications for ENT referral"

common_mistakes:
  - "Treating OME with antibiotics"
  - "Using standard-dose instead of high-dose amoxicillin"
  - "Forgetting to address pain control"
  - "Not considering observation option for eligible patients"
  - "Missing bilateral vs unilateral distinction"

red_flags:
  - "Mastoiditis (postauricular swelling, displaced pinna)"
  - "Facial nerve palsy"
  - "Signs of intracranial extension"
  - "Toxic appearance"

clinical_pearls:
  - "Bulging TM is the key finding - redness alone is not diagnostic"
  - "High-dose amoxicillin: 80-90 mg/kg/day divided BID"
  - "Observation option: >2 years, unilateral, non-severe, reliable follow-up"
  - "Pain control often more important than antibiotics to families"
  - "Treat for 10 days if <2 years, 5-7 days if >2 years with mild disease"

key_history_questions:
  - "Ear tugging or pain?"
  - "Fever - how high and how long?"
  - "Recent upper respiratory symptoms?"
  - "Previous ear infections? How many?"
  - "Recent antibiotics?"
  - "Daycare attendance?"
  - "Allergies to medications?"

key_exam_findings:
  - "TM position (bulging vs retracted vs neutral)"
  - "TM color (erythematous, yellow, normal)"
  - "TM mobility (pneumatic otoscopy)"
  - "Presence of effusion"
  - "Mastoid tenderness"
  - "Cervical lymphadenopathy"

treatment_principles:
  - "First-line: High-dose amoxicillin 80-90 mg/kg/day"
  - "Penicillin allergy (non-severe): Cefdinir"
  - "Penicillin allergy (severe): Azithromycin"
  - "Treatment failure: Amoxicillin-clavulanate or ceftriaxone IM"
  - "Pain: Ibuprofen or acetaminophen; topical benzocaine if >2 years"

disposition_guidance:
  - "Outpatient: Most cases"
  - "Observation option: >2 years, unilateral, non-severe, reliable follow-up"
  - "Reassess: 48-72 hours if no improvement"
  - "ENT referral: Recurrent AOM (3+ in 6 months, 4+ in 12 months)"
  - "ENT referral: Chronic OME >3 months with hearing concerns"

parent_styles:
  - anxious
  - experienced
  - antibiotic-seeking
  - antibiotic-hesitant

sources:
  - "AAP Clinical Practice Guideline: AOM (2013)"
  - "AAP Red Book"
```

---

## Conditions Covered

Echo includes **124 teaching frameworks** across pediatric medicine.

### By Category

#### Infectious Disease (25)
| Condition | Key Teaching Points |
|-----------|---------------------|
| Acute Otitis Media | Bulging TM, high-dose amoxicillin, observation option |
| Strep Pharyngitis | Centor criteria, rapid strep, penicillin first-line |
| Bronchiolitis | Supportive care only, no bronchodilators routine |
| Pneumonia | Distinguish viral vs bacterial, amoxicillin for CAP |
| UTI | Catheterized specimen in non-toilet trained, imaging |
| Croup | Steeple sign, dexamethasone, racemic epi for severe |
| Gastroenteritis | Oral rehydration, no antibiotics for viral |
| Influenza | Oseltamivir timing, high-risk groups |
| Pertussis | Macrolides, post-exposure prophylaxis |
| Mononucleosis | Heterophile antibody, avoid contact sports |
| Hand-Foot-Mouth | Supportive care, dehydration risk |
| Roseola | Fever then rash, febrile seizure risk |
| Fifth Disease | Slapped cheek, pregnancy risk |
| HSV Gingivostomatitis | Acyclovir for severe, dehydration |
| Conjunctivitis | Bacterial vs viral vs allergic |
| Sinusitis | AAP criteria (persistent, severe, worsening) |
| Oral Thrush | Nystatin, treat mother if breastfeeding |
| Impetigo | MRSA coverage, topical vs oral |
| Tinea Capitis | Oral antifungal required |
| Varicella | Supportive care, complications |
| Periorbital/Orbital Cellulitis | Distinguish types, CT for orbital |
| Meningitis | Lumbar puncture, empiric antibiotics |
| Lyme Disease | Erythema migrans, doxycycline |
| Cervical Lymphadenopathy | Bilateral vs unilateral, red flags |
| Pinworms | Tape test, treat household |

#### Respiratory (8)
| Condition | Key Teaching Points |
|-----------|---------------------|
| Asthma | Step therapy, action plans, controller vs rescue |
| Chronic Cough | >4 weeks, wet vs dry, workup approach |
| Allergic Rhinitis | Intranasal steroids first-line |
| Anaphylaxis | Epinephrine first, biphasic reactions |
| Foreign Body Aspiration | Rigid bronchoscopy |

#### Dermatology (15)
| Condition | Key Teaching Points |
|-----------|---------------------|
| Atopic Dermatitis | Moisturizers, topical steroids, flare management |
| Acne | Benzoyl peroxide, retinoids, when to refer |
| Diaper Dermatitis | Barrier cream, candida vs irritant |
| Seborrheic Dermatitis | Cradle cap, antifungal shampoo |
| Contact Dermatitis | Identify allergen, topical steroids |
| Molluscum | Self-limited, treatment options |
| Warts | Salicylic acid, cryotherapy |
| Scabies/Lice | Permethrin, household treatment |
| Pityriasis Rosea | Herald patch, self-limited |
| Infantile Hemangiomas | Observation vs propranolol |
| Alopecia | Tinea vs alopecia areata |

#### Mental Health/Behavioral (10)
| Condition | Key Teaching Points |
|-----------|---------------------|
| ADHD | DSM criteria, multimodal treatment |
| Anxiety | CBT first-line, SSRIs for severe |
| Depression | PHQ-A screening, safety assessment |
| Autism Spectrum | Early identification, M-CHAT |
| Suicidal Ideation | Safety planning, means restriction, hospitalization criteria |
| Substance Use | CRAFFT screening, brief intervention |
| Eating Disorders | Medical complications, when to hospitalize |
| Tics/Tourette | Reassurance, CBIT, medication options |
| Sleep Disorders | Sleep hygiene, behavioral interventions |
| Screen Time | AAP guidelines, family media plan |

#### Gastrointestinal (10)
| Condition | Key Teaching Points |
|-----------|---------------------|
| Constipation | Rome criteria, disimpaction, maintenance |
| GERD | Lifestyle modifications, PPI when indicated |
| Appendicitis | Pediatric appendicitis score, imaging |
| Intussusception | Currant jelly stool, air enema reduction |
| Celiac Disease | TTG-IgA screening, biopsy confirmation |
| IBD | Distinguish UC vs Crohn, growth monitoring |
| Functional Abdominal Pain | Rome IV, biopsychosocial model |
| Pyloric Stenosis | Projectile vomiting, olive mass, ultrasound |

#### Neurology (8)
| Condition | Key Teaching Points |
|-----------|---------------------|
| Febrile Seizures | Simple vs complex, parent counseling |
| Headache/Migraine | Red flags, abortive vs preventive |
| Breath-Holding Spells | Benign, iron deficiency check |
| Night Terrors | Non-REM parasomnia, reassurance |
| Syncope | Vasovagal vs cardiac, ECG for all |
| Speech Delay | Early intervention referral |
| Learning Disabilities | Educational evaluation |

#### Musculoskeletal (10)
| Condition | Key Teaching Points |
|-----------|---------------------|
| Limping Child | Age-based differential, septic joint emergency |
| Nursemaid's Elbow | Reduction technique, no X-ray needed |
| Growing Pains | Nighttime, bilateral, normal exam |
| Apophysitis | Osgood-Schlatter, Sever disease |
| Scoliosis | Adam's forward bend, Cobb angle |
| JIA | Morning stiffness, uveitis screening |
| Torticollis | CMT vs acquired, PT referral |
| DDH | Barlow/Ortolani, ultrasound timing |
| HSP | Palpable purpura, renal monitoring |

#### Neonatal/Infant (15)
| Condition | Key Teaching Points |
|-----------|---------------------|
| Febrile Infant | Age-based approach, Rochester/Philadelphia criteria |
| Hyperbilirubinemia | Phototherapy thresholds, exchange transfusion |
| Neonatal Hypoglycemia | Risk factors, glucose targets |
| Early-Onset Sepsis | Kaiser calculator, empiric antibiotics |
| Breastfeeding Issues | Latch assessment, supplementation |
| CMPI | Elimination diet, extensively hydrolyzed formula |
| Colic | Rule of 3s, parent support |
| Failure to Thrive | Organic vs non-organic, catch-up growth |
| Tongue Tie | Feeding assessment, frenotomy indications |
| Umbilical Issues | Hernia natural history, granuloma treatment |
| Safe Sleep/SIDS | ABCs of safe sleep |
| Teething | What's NOT teething, safe remedies |
| Benign Neonatal Rashes | ETN, milia, salmon patches |

#### Endocrine/Metabolic (8)
| Condition | Key Teaching Points |
|-----------|---------------------|
| Obesity | BMI percentiles, comorbidity screening |
| Type 2 Diabetes | Metformin, lifestyle modification |
| Type 1 Diabetes Sick Day | Ketone monitoring, insulin adjustment |
| Thyroid Disorders | TSH screening, when to treat |
| Short Stature | Growth velocity, bone age |
| Puberty Disorders | Precocious vs delayed, workup |
| Adrenal Insufficiency | Stress dosing, emergency management |

#### Genitourinary (8)
| Condition | Key Teaching Points |
|-----------|---------------------|
| Enuresis | Primary vs secondary, alarm therapy |
| Cryptorchidism | Surgical timing, cancer risk |
| Phimosis | Physiologic vs pathologic, topical steroids |
| Acute Scrotum | Testicular torsion emergency |
| Inguinal Hernia/Hydrocele | Surgical referral timing |
| Hematuria/Proteinuria | Transient vs persistent, workup |
| Hypertension | Percentile-based diagnosis |

#### Emergency/Trauma (8)
| Condition | Key Teaching Points |
|-----------|---------------------|
| Head Injury | PECARN criteria, CT decision rules |
| Ingestions | Poison control, decontamination |
| Burns | Fluid resuscitation, transfer criteria |
| Drowning | Submersion vs immersion, pulmonary edema |
| Animal Bites | Prophylactic antibiotics, rabies |
| Child Abuse | Sentinel injuries, mandatory reporting |
| Epistaxis | Anterior vs posterior, first aid |
| Foreign Body (Ear/Nose) | Button battery emergency |

#### Other (7)
| Condition | Key Teaching Points |
|-----------|---------------------|
| Kawasaki Disease | Diagnostic criteria, IVIG timing, echo |
| Innocent Murmurs | Still's murmur, when to refer |
| Chest Pain | Rarely cardiac in children |
| Iron Deficiency Anemia | Screening, oral iron dosing |
| Oncologic Emergencies | Fever/neutropenia, tumor lysis |
| Food Allergy Prevention | Early introduction |
| Recurrent Infections | Normal vs immunodeficiency |

---

## API Reference

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create new account |
| POST | `/auth/login` | Login, receive tokens |
| POST | `/auth/refresh` | Refresh access token |
| POST | `/auth/logout` | Invalidate tokens |
| GET | `/auth/me` | Get current user profile |
| PATCH | `/auth/me` | Update profile |
| GET | `/auth/me/stats` | Get user's case statistics |

### Case Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/case/frameworks` | List available conditions |
| POST | `/case/start` | Start case (static generation) |
| POST | `/case/start/dynamic` | Start case (Claude generation) |
| POST | `/case/message` | Send message during case |
| POST | `/case/debrief` | Get case debrief |
| POST | `/case/export` | Export case with materials |
| GET | `/case/history` | List completed cases |
| GET | `/case/{session_id}` | Resume/view case |
| GET | `/case/{session_id}/debrief` | Get structured debrief |
| POST | `/case/{session_id}/question` | Ask follow-up question |

### Admin Endpoints (requires admin role)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/users` | List all users |
| GET | `/admin/users/{id}` | User details |
| GET | `/admin/cases` | List all cases |
| GET | `/admin/cases/{session_id}` | Case details with transcript |
| GET | `/admin/metrics` | Platform metrics |
| GET | `/admin/metrics/struggles` | Learning struggle analysis |

### Patient Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/patients/import` | Import C-CDA XML |
| GET | `/patients` | List imported patients |
| GET | `/patients/{id}` | Patient details |
| DELETE | `/patients/{id}` | Delete patient |

### Framework Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/frameworks` | List all frameworks |
| GET | `/frameworks/categories` | Categories with counts |
| GET | `/frameworks/category/{cat}` | Frameworks by category |
| GET | `/frameworks/{key}` | Specific framework |

### Feedback Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/feedback` | Get feedback on action |
| POST | `/question` | Get Socratic question |
| POST | `/debrief` | Get encounter debrief |

---

## Authentication & Roles

### User Levels (Learner Type)

```python
class LearnerLevel(str, Enum):
    STUDENT = "student"       # Medical student (MS1-MS4)
    RESIDENT = "resident"     # Pediatric resident (PGY1-3)
    NP_STUDENT = "np_student" # Nurse practitioner student
    FELLOW = "fellow"         # Fellowship trainee
    ATTENDING = "attending"   # Practicing physician
```

Cases adapt complexity and expectations based on level.

### User Roles (Access Control)

```python
class UserRole(str, Enum):
    LEARNER = "learner"  # Default - can use cases
    ADMIN = "admin"      # Access to /admin endpoints
```

### JWT Token Structure

```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "role": "learner",
  "type": "access",
  "exp": 1234567890
}
```

- Access tokens: 24 hour expiration
- Refresh tokens: 7 day expiration

---

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    level VARCHAR(50) DEFAULT 'student',
    role VARCHAR(50) DEFAULT 'learner',
    specialty_interest VARCHAR(255),
    institution VARCHAR(255),
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP
);
```

### Case Sessions Table

```sql
CREATE TABLE case_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    condition_key VARCHAR(100) NOT NULL,
    condition_display VARCHAR(255),
    patient_data JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    phase VARCHAR(50) DEFAULT 'intro',
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    duration_seconds INTEGER,
    history_gathered TEXT[],
    exam_performed TEXT[],
    differential TEXT[],
    plan_proposed TEXT[],
    hints_given INTEGER DEFAULT 0,
    teaching_moments TEXT[],
    debrief_summary TEXT,
    learning_materials JSONB
);
```

### Messages Table

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES case_sessions(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,  -- 'user' or 'echo'
    content TEXT NOT NULL,
    phase VARCHAR(50),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Configuration

### Required Environment Variables

```bash
# Claude API (required)
ANTHROPIC_API_KEY=sk-ant-...

# Database (required for persistence)
DATABASE_URL=postgresql://user:pass@host:5432/echo

# JWT Secret (required for auth)
JWT_SECRET=your-secure-secret-key
```

### Optional Environment Variables

```bash
# Voice features
ELEVEN_API_KEY=...      # Eleven Labs text-to-speech
DEEPGRAM_API_KEY=...    # Deepgram speech-to-text

# Citation search
EXA_API_KEY=...         # Medical literature search

# Server config
ECHO_HOST=0.0.0.0
ECHO_PORT=8001
```

### Claude Model Configuration

Default: `claude-sonnet-4-5-20250929`

Can be changed in `src/config.py`:

```python
claude_model: str = "claude-sonnet-4-5-20250929"
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL (optional, for persistence)
- Anthropic API key

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/echo.git
cd echo

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run server
uvicorn src.main:app --reload --port 8001
```

### Quick Test

```bash
# Check health
curl http://localhost:8001/health

# Register a user
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "name": "Test User"}'

# Login
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Start a case (use token from login)
curl -X POST http://localhost:8001/case/start/dynamic \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"learner_level": "student", "condition_key": "otitis_media"}'
```

---

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/
COPY knowledge/ knowledge/

EXPOSE 8001
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

### Replit

1. Import from GitHub
2. Set environment variables in Secrets
3. Run command: `uvicorn src.main:app --host 0.0.0.0 --port 8001`

### Railway/Render

1. Connect GitHub repository
2. Set environment variables
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

---

## Contributing

### Adding New Conditions

1. Create framework file in `knowledge/frameworks/`:

```yaml
# knowledge/frameworks/new_condition.yaml
topic: "Condition Name"
aliases: ["alias1", "alias2"]
category: infectious  # or respiratory, GI, etc.
age_range_months: [0, 216]

teaching_goals:
  - "Goal 1"
  - "Goal 2"

common_mistakes:
  - "Mistake 1"

red_flags:
  - "Red flag 1"

clinical_pearls:
  - "Pearl 1"

key_history_questions:
  - "Question 1"

key_exam_findings:
  - "Finding 1"

treatment_principles:
  - "Treatment 1"

disposition_guidance:
  - "Disposition 1"

parent_styles: [anxious, experienced]

sources:
  - "AAP Guidelines"
```

2. Framework is automatically loaded on next startup

### Improving Prompts

Prompts are in `src/prompts/`:

- `system_prompt.md` - Main tutor personality
- `feedback_prompt.md` - Feedback generation
- `debrief_prompt.md` - Debrief generation

### Code Style

- Python 3.11+ type hints
- Pydantic v2 models
- FastAPI async/await patterns
- 2-space indentation (project standard)

---

## Roadmap

### Planned Features

- [ ] **Spaced repetition** - Review cases at optimal intervals
- [ ] **Competency mapping** - Track ACGME milestones
- [ ] **Multi-modal cases** - Images, X-rays, lab results
- [ ] **Peer comparison** - Anonymous benchmarking
- [ ] **Custom case creation** - Instructors create cases
- [ ] **LMS integration** - SCORM/LTI compatibility
- [ ] **Mobile app** - iOS/Android native apps
- [ ] **Voice mode** - Full voice-based case interactions

### Known Limitations

1. Patient import is in-memory only (not persisted to database)
2. No image/media support in cases yet
3. Voice features require additional API keys
4. Frontend needs updates for new features

---

## License

MIT License - See LICENSE file for details.

---

## Contact

For questions, issues, or contributions:

- GitHub Issues: [github.com/your-org/echo/issues](https://github.com/your-org/echo/issues)
- Email: your-email@example.com

---

*Echo is part of the MedEd Platform, alongside Oread (patient generation), Syrinx (voice encounters), and Mneme (EMR interface).*
