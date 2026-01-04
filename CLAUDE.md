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

## Metis Integration

Echo is part of the **MedEd Platform**, orchestrated by Metis.

### Platform Overview

| Project | Greek Name | Port | Purpose |
|---------|------------|------|---------|
| synpat | Oread | 8004 | Patient generation |
| synvoice | Syrinx | 8003 | Encounter scripts |
| synchart | Mneme | 8002 | EMR interface |
| echo | **Echo** | 8001 | AI tutor |
| metis | Metis | 3000 | Portal (planned) |

### Shared Models

Echo uses shared models generated by Metis:

```bash
# Regenerate shared models after schema changes
cd /Users/dochobbs/Downloads/Consult/MedEd/metis/shared
python sync.py --project echo
```

Generated models location: `src/models/_generated/context.py`

### Starting with Metis

```bash
# Start all MedEd services at once
cd /Users/dochobbs/Downloads/Consult/MedEd/metis/scripts
./start-all.sh

# Check status
./status.sh

# Stop all
./stop-all.sh
```

### Standalone Mode

Echo can run independently without Metis:

```bash
cd /Users/dochobbs/Downloads/Consult/MedEd/echo
source .venv/bin/activate
uvicorn src.main:app --port 8001
# API at http://localhost:8001
```

### Data Flow

```
Oread/Syrinx/Mneme → [PatientContext/EncounterContext] → Echo
                                                           ↓
                                                    [Socratic Feedback]
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
| **Metis** | `metis/` | Platform orchestration |
| Oread | `synpat/` | Patient generation |
| Syrinx | `synvoice/` | Voice encounters |
| Mneme | `synchart/` | EMR interface |

## UI Resources

### Animated Icons - Its Hover

**Source:** https://www.itshover.com/icons

Animated icons for UI components. Relevant icons for Echo/MedEd:

**Medical/Health:**
- Ambulance, Heart, Scan Heart, Shield Check, Bulb

**Communication:**
- Message Circle, Send, Send Horizontal, Mail Filled, Bell, Filled Bell, Bell Off

**Status/Feedback:**
- Checked, Simple Checked, Double Check, Filled Checked, Rosette Discount Check
- Triangle Alert, Info Circle, Question Mark

**Actions:**
- Refresh, Expand, External Link, Copy, Trash, Pen, Toggle

**Users:**
- User Check, User Plus, Users, Users Group

**Media:**
- Player, Volume 2, Volume X, Camera, Camera Off, Eye, Eye Off

**Navigation:**
- Arrow Narrow Right, Arrow Narrow Left, Arrow Back, Down Cheveron, Right Cheveron
- Home, Logout, Magnifier

**Learning/Progress:**
- Book, Bookmark, History Circle, Star, Target, Sparkles, Rocket

**Full icon list:**
Accessibility, Alarm Clock Plus, Align Center, Align Vertical Space Around, Ambulance, Angry, Annoyed, Apple Brand Logo, Arrow Back, Arrow Back Up, Arrow Big Left Dash, Arrow Big Left, Arrow Big Right Dash, Arrow Big Right, Arrow Big Up Dash, Arrow Big Up, Arrow Down 1-0, Arrow Down A-Z, Arrow Narrow Down Dashed, Arrow Narrow Down, Arrow Narrow Left Dashed, Arrow Narrow Left, Arrow Narrow Right Dashed, Arrow Narrow Right, Arrow Narrow Up Dashed, Arrow Narrow Up, At Sign, Banana, Battery Charging, Battery, Battery Pause, Bell Off, Bluetooth Connected, Book, Bookmark, Brand Google, Brightness Down, Bulb, Camera, Camera Off, Candy Cane, Cart, Chart Bar, Chart Covariate, Chart Histogram, Chart Line, Chart Pie, Checked, Clock, Code, Code XML, Coffee, Copy, Copy Off, CPU, Credit Card, Currency Bitcoin, Currency Dollar, Currency Ethereum, Currency Euro, Currency Rupee, Device Airpods, Dialpad, Discord, Docker, Dots Horizontal, Dots Vertical, Double Check, Down Cheveron, Drum, Expand, External Link, Eye, Eye Off, Facebook, Figma, File Description, Filled Bell, Filled Checked, Flame, Focus, Gauge, Gear, Ghost, GitHub Copilot, GitHub, GitLab, Globe, Gmail, Hand Heart, Hashtag, Heart, History Circle, Home, Info Circle, Instagram, JavaScript, Keyframes, Layers, Layout Bottombar Collapse, Layout Sidebar Right, Like, Link, LinkedIn, Lock, Logout, Magnifier, Mail Filled, Meh, Message Circle, Moon, Mouse Pointer 2, MySQL, Node.js, Paint, Party Popper, Pen, Phone Volume, Pinterest, Player, Plug Connected, Plug Connected X, Python, QR Code, Question Mark, Radio, Rainbow, Refresh, Right Cheveron, Rocket, Rosette Discount Check, Rosette Discount, Router, Satellite Dish, Scan Barcode, Scan Heart, Send Horizontal, Send, Shield Check, Shopping Cart, Simple Checked, Skull Emoji, Slack, Snapchat, Soup, Sparkles, Spotify, Stack 3, Stack, Star, Subscript, Target, Telephone, Terminal, Toggle, Trash, Triangle Alert, Truck Electric, Twitter, Twitter X, TypeScript, Unlink, Unordered List, User Check, User Plus, Users Group, Users, Vercel, Vinyl, Volume 2, Volume X, Washing Machine, WhatsApp, WiFi, WiFi Off, World, X, YouTube
