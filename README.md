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

## Widget Integration

Embed Echo in your MedEd app:

```bash
npm install @meded/echo-widget
```

```tsx
import { EchoWidget } from '@meded/echo-widget';
import '@meded/echo-widget/styles.css';

<EchoWidget
  apiUrl="http://localhost:8001"
  context={{
    source: 'oread',  // or 'syrinx' or 'mneme'
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

See [docs/WIDGET_INTEGRATION.md](docs/WIDGET_INTEGRATION.md) for full documentation.

### Local Development (widget not yet on npm)

```bash
# In echo/widget
npm link

# In host app
npm link @meded/echo-widget
```

Or in host app's `package.json`:
```json
{
  "dependencies": {
    "@meded/echo-widget": "file:../echo/widget"
  }
}
```

## Tech Stack

- FastAPI + Pydantic v2
- Claude (Anthropic) for clinical reasoning
- Eleven Labs for voice output
- Deepgram/Whisper for voice input

## Available Voices

| Voice | Description |
|-------|-------------|
| `eryn` | Calm, confident (default) |
| `matilda` | Warm, friendly |
| `clarice` | Clear, professional |
| `clara` | Approachable |
| `devan` | Energetic |
| `lilly` | Gentle |
