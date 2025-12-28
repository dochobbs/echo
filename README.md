# Echo

AI Attending Tutor for Medical Education.

Echo provides Socratic feedback and clinical teaching across the MedEd platform ecosystem:
- **Oread** - Patient chart review
- **Syrinx** - Voice encounter coaching
- **Mneme** - EMR decision support

## Quick Start

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run
uvicorn src.main:app --reload --port 8001
```

## API

### POST /feedback
Get feedback on a learner action (order, diagnosis, question).

### POST /question
Get a Socratic question about the current case.

### POST /debrief
Get comprehensive post-encounter feedback.

## Tech Stack

- FastAPI + Pydantic v2
- Claude (Anthropic) for clinical reasoning
- Eleven Labs for voice output
- Deepgram/Whisper for voice input
