# Echo Handoff Document

**Created:** December 28, 2025
**For:** New Claude Code instance

## Project Summary

**Echo** is an AI attending/tutor service that provides Socratic feedback across the MedEd platform ecosystem. It's a standalone FastAPI service that Oread, Syrinx, and Mneme all connect to.

## Current State: Scaffolded, Not Running

The project structure is created with:
- FastAPI app skeleton
- Pydantic models for requests/responses
- Core tutor module with Claude integration
- API endpoints (feedback, question, debrief)

**NOT yet implemented:**
- Eleven Labs TTS integration
- Deepgram/Whisper STT integration
- WebSocket for real-time voice
- Git repo initialization
- Testing beyond model tests

## Related Projects (Same Ecosystem)

| Project | Path | Purpose |
|---------|------|---------|
| **Oread** | `/Users/dochobbs/Downloads/Consult/MedEd/synpat` | Synthetic patient generator |
| **Syrinx** | `/Users/dochobbs/Downloads/Consult/MedEd/synvoice` | Voice encounter scripts + TTS |
| **Mneme** | `/Users/dochobbs/Downloads/Consult/MedEd/synchart` | Fake EMR interface |
| **Echo** | `/Users/dochobbs/Downloads/Consult/MedEd/echo` | AI tutor (this project) |

## Quick Start

```bash
cd /Users/dochobbs/Downloads/Consult/MedEd/echo

# Setup venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure (copy and edit)
cp .env.example .env
# Add ANTHROPIC_API_KEY, ELEVEN_LABS_API_KEY

# Run
uvicorn src.main:app --reload --port 8001

# Test
curl http://localhost:8001/health
```

## Key Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Full development context |
| `src/main.py` | FastAPI app entry |
| `src/core/tutor.py` | Claude integration, core logic |
| `src/models/context.py` | `PatientContext` - shared data format |
| `src/models/feedback.py` | Request/response models |
| `src/prompts/socratic.md` | Teaching philosophy |

## Architecture Decision: Hybrid Voice

We decided on **hybrid** approach:
- **Claude** handles clinical reasoning + Socratic dialogue
- **Eleven Labs** handles voice synthesis (TTS)
- **Deepgram/Whisper** handles voice input (STT)

This gives better control over clinical accuracy than a full Eleven Labs conversational agent.

## API Endpoints

```
POST /feedback     - Feedback on learner action
POST /question     - Socratic question about case
POST /debrief      - Post-encounter analysis
GET  /health       - Health check

(Planned)
WS   /conversation - Real-time voice dialogue
```

## Shared Context Protocol

All platforms send patient data to Echo in this format:

```python
PatientContext(
    patient_id: str,
    source: "oread" | "syrinx" | "mneme",
    name: str,
    age_years: int,
    problem_list: list[Condition],
    medication_list: list[Medication],
    allergy_list: list[Allergy],  # Critical for safety
    recent_encounters: list[EncounterSummary],
)
```

## Priority Next Steps

1. **Initialize git repo**
   ```bash
   git init
   git add -A
   git commit -m "Initial Echo scaffold"
   ```

2. **Add Eleven Labs TTS**
   - Create `src/core/voice_out.py`
   - Add endpoint to return audio URLs
   - Choose/configure Echo's voice

3. **Add Deepgram STT**
   - Create `src/core/voice_in.py`
   - For real-time transcription

4. **WebSocket endpoint**
   - Create `src/routers/voice.py`
   - Real-time voice conversation

5. **Test with Oread**
   - Generate patient in Oread
   - Send to Echo for feedback
   - Verify integration works

## Design Principles

From CLAUDE.md:
1. **Socratic First**: Never give direct answers unless safety-critical
2. **Context-Aware**: Adapt feedback to learner level
3. **Specific**: Reference exact patient data in feedback
4. **Encouraging**: Build confidence while correcting errors
5. **Medical Accuracy**: Clinical content must be correct

## Environment Variables Needed

```bash
ANTHROPIC_API_KEY=sk-ant-...     # Required
ELEVEN_LABS_API_KEY=...          # For TTS
ECHO_VOICE_ID=...                # Eleven Labs voice
DEEPGRAM_API_KEY=...             # For STT (optional, can use Whisper)
```

## Questions to Resolve

1. Which Eleven Labs voice for Echo? (warm, authoritative attending)
2. Should Echo have different voices for different modes?
3. How should errors from Syrinx scenarios be surfaced to Echo?
4. Should Echo persist conversation history?

## Files Not Yet Created

- `src/core/voice_out.py` - Eleven Labs TTS
- `src/core/voice_in.py` - Deepgram/Whisper STT
- `src/routers/voice.py` - WebSocket endpoint
- `src/prompts/feedback.md` - Feedback prompt template
- `src/prompts/debrief.md` - Debrief prompt template

---

**Ready to continue development in a fresh Claude Code instance.**
