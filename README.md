# Echo

**AI Attending Tutor for Medical Education**

Echo provides Socratic clinical teaching across the MedEd platform. It never gives direct answers -- instead, it asks guiding questions that help learners develop clinical reasoning.

Part of the **MedEd Platform** -- see [metis/](../metis/) for platform orchestration.

**Port:** 8001

---

## Design Principles

1. **Socratic First** -- Ask questions, don't give answers (unless safety-critical)
2. **Context-Aware** -- Adapt feedback to learner level (student, resident, NP student)
3. **Specific** -- Reference exact patient data in feedback ("I notice this patient has a penicillin allergy...")
4. **Encouraging** -- Build confidence while correcting errors
5. **Medically Accurate** -- All clinical content must be correct

## Features

- **Socratic Feedback** -- Guiding questions on learner actions
- **Case-Based Learning** -- Dynamic case generation from 160+ clinical frameworks
- **Post-Encounter Debrief** -- Comprehensive review after encounters
- **Voice I/O** -- Real-time voice dialogue via WebSocket
- **Embeddable Widget** -- Drop-in React component for any MedEd app
- **Patient Import** -- C-CDA document import for case context
- **Framework Library** -- Curated clinical reasoning frameworks

## Quick Start

```bash
cd echo
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run
uvicorn src.main:app --reload --port 8001
# API at http://localhost:8001
# Docs at http://localhost:8001/docs
```

## API Endpoints

### Core Tutoring (REST)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/feedback` | POST | Get feedback on a learner action |
| `/question` | POST | Get a Socratic question about current case |
| `/debrief` | POST | Full post-encounter analysis |
| `/health` | GET | Health check |

### Case System

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/cases/start/dynamic` | POST | Start a dynamically generated case |
| `/cases/{id}/interact` | POST | Submit learner action in a case |
| `/cases/{id}/history` | GET | Get case interaction history |

### Patient Import

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/patients/import` | POST | Import C-CDA patient document |
| `/patients/{id}` | GET | Get imported patient |
| `/patients` | GET | List imported patients |

### Frameworks

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/frameworks` | GET | List available clinical frameworks |
| `/frameworks/{id}` | GET | Get framework details |

### Voice (WebSocket)

| Endpoint | Description |
|----------|-------------|
| `/voice/conversation` | Real-time voice dialogue with Echo |

**Note:** Echo routes have **no `/api/` prefix**. This differs from other MedEd services.

## Tutor Modes

Echo operates in different modes based on the learning context:

| Mode | Trigger | Behavior |
|------|---------|----------|
| **Observer** | Watching encounter | Silent observation, notes issues for later |
| **Socratic** | Learner asks for help | Questions that guide clinical reasoning |
| **Feedback** | After a learner action | Specific feedback on the decision |
| **Debrief** | End of encounter | Comprehensive review with teaching points |

## Request Format

All tutoring endpoints accept patient context in a flat format:

```json
{
  "learner_question": "What antibiotic should I prescribe?",
  "patient": {
    "patient_id": "abc-123",
    "source": "oread",
    "name": "Marcus Johnson",
    "age_years": 2,
    "age_months": 24,
    "sex": "male",
    "problem_list": [
      {"display_name": "Acute Otitis Media", "is_active": true, "code": "65363002"}
    ],
    "medication_list": [],
    "allergy_list": [
      {"allergen": "Penicillin", "reaction": "rash"}
    ]
  }
}
```

Echo will respond with Socratic guidance:

> "Before we jump to treatment, let's think about what you're treating. You mentioned otitis media -- but I notice something in the allergy list. What would that change about your antibiotic choice?"

## Widget Integration

Embed Echo in any MedEd app:

```tsx
import { EchoWidget } from '@meded/echo-widget';
import '@meded/echo-widget/styles.css';

<EchoWidget
  apiUrl="http://localhost:8001"
  context={{
    source: 'oread',
    patient: {
      patientId: patient.id,
      name: patient.name,
      age: patient.age,
    },
    learnerLevel: 'resident',
  }}
  defaultVoice="eryn"
  position="bottom-right"
/>
```

For local development (widget not yet on npm):

```bash
# In echo/widget
npm link

# In host app
npm link @meded/echo-widget
```

See [docs/WIDGET_INTEGRATION.md](docs/WIDGET_INTEGRATION.md) for full documentation.

## Voice Configuration

### Available Voices (ElevenLabs)

| Voice | Description |
|-------|-------------|
| `eryn` | Calm, confident (default) |
| `matilda` | Warm, friendly |
| `clarice` | Clear, professional |
| `clara` | Approachable |
| `devan` | Energetic |
| `lilly` | Gentle |

### Speech-to-Text

- Deepgram Nova-2 (cloud) or Whisper large-v3 (local)
- Medical vocabulary boosting enabled
- Language: en-US

## Project Structure

```
echo/
├── src/
│   ├── main.py              # FastAPI app (router mounts)
│   ├── config.py            # Settings (API keys, models)
│   ├── models/              # Pydantic models
│   │   ├── context.py       # PatientContext, EncounterContext
│   │   ├── feedback.py      # FeedbackRequest/Response
│   │   └── conversation.py  # Message, Turn, Session
│   ├── routers/
│   │   ├── feedback.py      # POST /feedback
│   │   ├── question.py      # POST /question
│   │   ├── debrief.py       # POST /debrief
│   │   └── voice.py         # WebSocket /voice/conversation
│   ├── cases/
│   │   ├── router.py        # Case endpoints
│   │   ├── generator.py     # Case generation
│   │   ├── dynamic_generator.py  # Dynamic case from frameworks
│   │   ├── models.py        # Case models
│   │   ├── history.py       # Case history
│   │   └── persistence.py   # Case storage
│   ├── frameworks/
│   │   └── router.py        # Framework endpoints
│   ├── patients/
│   │   └── router.py        # Patient import/retrieval
│   ├── auth/
│   │   └── router.py        # Authentication
│   ├── admin/
│   │   └── router.py        # Admin endpoints
│   ├── prompts/
│   │   ├── system.md        # System prompt
│   │   ├── socratic.md      # Socratic questioning
│   │   ├── feedback.md      # Feedback generation
│   │   ├── question.md      # Question generation
│   │   └── debrief.md       # Debrief generation
│   └── core/
│       ├── tutor.py         # Claude-based Socratic tutor
│       ├── voice_in.py      # STT (Deepgram/Whisper)
│       └── voice_out.py     # TTS (ElevenLabs)
├── widget/                  # Embeddable React component
├── docs/
│   ├── WIDGET_INTEGRATION.md
│   └── PROJECT_DOCUMENTATION.md
├── tests/
├── requirements.txt
├── .env.example
└── CLAUDE.md
```

## Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...       # Claude API

# Required for voice output
ELEVEN_LABS_API_KEY=...             # ElevenLabs TTS
ECHO_VOICE_ID=...                  # Default voice ID

# Optional for voice input
DEEPGRAM_API_KEY=...               # Deepgram STT

# Optional for persistence
DATABASE_URL=...                   # SQLite or PostgreSQL
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.12+, FastAPI, Pydantic v2 |
| **LLM** | Claude (Anthropic) -- clinical reasoning + Socratic dialogue |
| **TTS** | ElevenLabs -- voice synthesis |
| **STT** | Deepgram or Whisper -- voice input |
| **Transport** | REST + WebSocket for real-time voice |

## Cross-Service Integration

Echo receives patient data from all MedEd services:

```
Oread  --[PatientContext]--> Echo /question, /feedback, /debrief
Syrinx --[EncounterContext]-> Echo /debrief
Mneme  --[PatientContext]--> Echo (via EchoClient)
Metis  --[PatientContext]--> Echo /question (via Vite proxy)
```

Echo had **zero code changes** in the February 2026 integration work. Its existing endpoints already accept the `PatientContext` format with `source: "oread"`.

See [docs/INTEGRATION.md](../docs/INTEGRATION.md) for the full integration guide.

## Documentation

- [WIDGET_INTEGRATION.md](docs/WIDGET_INTEGRATION.md) -- Embedding Echo in apps
- [PROJECT_DOCUMENTATION.md](docs/PROJECT_DOCUMENTATION.md) -- Detailed project docs
- [CLAUDE.md](CLAUDE.md) -- Development context for AI assistants
- [Integration Guide](../docs/INTEGRATION.md) -- Cross-service data flow

## Development

```bash
source .venv/bin/activate
uvicorn src.main:app --reload --port 8001   # Dev server
pytest tests/                                # Tests
```

## License

Internal use only -- Medical education.
