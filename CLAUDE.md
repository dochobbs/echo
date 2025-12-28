# CLAUDE.md - Echo Development Context

**Last Updated:** December 2025

## Project Overview

**Echo** is an AI attending/tutor service that provides Socratic feedback across the MedEd platform ecosystem. It works with Oread (patient generation), Syrinx (voice encounters), and Mneme (EMR interface).

## Architecture

Echo is a **standalone service** that other platforms connect to:

```
┌─────────────────────────────────────────────────────────┐
│                        Echo                              │
│         FastAPI + Claude + Eleven Labs + Whisper         │
└────────────────┬──────────────┬──────────────┬──────────┘
                 │              │              │
        ┌────────┴───┐   ┌──────┴─────┐  ┌─────┴─────┐
        │   Oread    │   │   Syrinx   │  │   Mneme   │
        │ (patients) │   │  (voice)   │  │   (EMR)   │
        └────────────┘   └────────────┘  └───────────┘
```

## Tech Stack

- **Backend**: Python 3.12+, FastAPI, Pydantic v2
- **LLM**: Claude (Anthropic API) - clinical reasoning + Socratic dialogue
- **TTS**: Eleven Labs - voice synthesis for Echo's responses
- **STT**: Deepgram or Whisper - voice input transcription
- **Transport**: REST API + WebSocket for real-time voice

## Project Structure

```
echo/
├── src/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings (API keys, models)
│   ├── models/              # Pydantic models
│   │   ├── context.py       # PatientContext, EncounterContext
│   │   ├── feedback.py      # FeedbackRequest, FeedbackResponse
│   │   └── conversation.py  # Message, Turn, Session
│   ├── core/
│   │   ├── tutor.py         # Claude-based Socratic tutor
│   │   ├── voice_in.py      # STT integration (Deepgram/Whisper)
│   │   └── voice_out.py     # TTS integration (Eleven Labs)
│   ├── routers/
│   │   ├── feedback.py      # POST /feedback endpoints
│   │   ├── question.py      # POST /question endpoints
│   │   ├── debrief.py       # POST /debrief endpoints
│   │   └── voice.py         # WebSocket /conversation
│   └── prompts/
│       ├── socratic.md      # Socratic questioning prompt
│       ├── feedback.md      # Feedback generation prompt
│       └── debrief.md       # Post-encounter debrief prompt
├── tests/
│   └── test_tutor.py
├── pyproject.toml
├── requirements.txt
├── .env.example
├── CLAUDE.md
└── README.md
```

## API Endpoints

### Text-based (REST)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/feedback` | POST | Get feedback on a specific learner action |
| `/question` | POST | Get a Socratic question about current case |
| `/debrief` | POST | Full post-encounter analysis |
| `/health` | GET | Health check |

### Voice-based (WebSocket)

| Endpoint | Description |
|----------|-------------|
| `/conversation` | Real-time voice dialogue with Echo |

## Context Protocol

All platforms send patient context in a shared format:

```python
class PatientContext(BaseModel):
    """Shared patient context from any platform."""
    patient_id: str
    demographics: dict          # Name, age, sex
    problem_list: list[dict]    # Active conditions
    medication_list: list[dict] # Current medications
    allergy_list: list[dict]    # Known allergies
    recent_encounters: list[dict]  # Last 3-5 encounters
    source: Literal["oread", "syrinx", "mneme"]

class FeedbackRequest(BaseModel):
    """Request for feedback on learner action."""
    patient: PatientContext
    learner_action: str         # What the learner did/said
    action_type: str            # "diagnosis", "order", "question", "plan"
    learner_level: str          # "student", "resident", "np_student"
    context: Optional[str]      # Additional context
```

## Tutor Modes

Echo operates in different modes based on the situation:

| Mode | Trigger | Behavior |
|------|---------|----------|
| **Observer** | Watching encounter | Silent, notes issues |
| **Socratic** | Learner asks for help | Questions, doesn't give answers |
| **Feedback** | After action | Specific feedback on decision |
| **Debrief** | End of encounter | Comprehensive review |

## Voice Configuration

### Eleven Labs Voice

Echo should have a consistent, professional voice:
- Voice: TBD (warm, authoritative attending physician)
- Speed: Slightly slower than normal (pedagogical)
- Stability: High (consistent across sessions)

### Whisper/Deepgram Settings

- Model: whisper-large-v3 or deepgram-nova-2
- Language: en-US
- Medical vocabulary boost: enabled

## Integration Examples

### From Oread (chart review)
```python
# User clicks "Ask Echo" on a patient chart
response = echo.post("/feedback", json={
    "patient": patient_context,
    "learner_action": "I would start with reviewing the growth chart",
    "action_type": "assessment_start",
    "learner_level": "np_student"
})
# Echo: "Good instinct. What specifically on the growth chart caught your attention?"
```

### From Syrinx (during encounter)
```python
# Real-time coaching during simulated encounter
# Learner asks: "What antibiotic should I prescribe?"
response = echo.post("/question", json={
    "patient": patient_context,
    "learner_question": "What antibiotic should I prescribe?",
    "encounter_state": "plan_phase"
})
# Echo: "Before we jump to treatment, what's your differential?
#        What are you treating?"
```

### From Mneme (order review)
```python
# Learner places an order in the EMR
response = echo.post("/feedback", json={
    "patient": patient_context,
    "learner_action": "Ordered amoxicillin 250mg TID x10 days",
    "action_type": "medication_order",
    "learner_level": "resident"
})
# Echo: "I notice this patient has a documented penicillin allergy.
#        What would you do differently?"
```

## Development Commands

```bash
# Setup
cd /Users/dochobbs/Downloads/Consult/MedEd/echo
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Run server
uvicorn src.main:app --reload --port 8001

# Test
pytest tests/
```

## Environment Variables

```bash
ANTHROPIC_API_KEY=       # Claude API
ELEVEN_LABS_API_KEY=     # Eleven Labs TTS
DEEPGRAM_API_KEY=        # Deepgram STT (or use local Whisper)
ECHO_VOICE_ID=           # Eleven Labs voice ID for Echo
```

## Design Principles

1. **Socratic First**: Never give direct answers unless safety-critical
2. **Context-Aware**: Adapt feedback to learner level
3. **Specific**: Reference exact patient data in feedback
4. **Encouraging**: Build confidence while correcting errors
5. **Medical Accuracy**: Clinical content must be correct

## Related Projects

| Project | Path | Purpose |
|---------|------|---------|
| Oread | `/Users/dochobbs/Downloads/Consult/MedEd/synpat` | Patient generation |
| Syrinx | `/Users/dochobbs/Downloads/Consult/MedEd/synvoice` | Voice encounters |
| Mneme | `/Users/dochobbs/Downloads/Consult/MedEd/synchart` | EMR interface |
