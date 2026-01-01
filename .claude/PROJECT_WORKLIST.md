# Echo Project Worklist

**Last Updated:** 2026-01-01

## Completed

- [x] Git repo setup and initial scaffold
- [x] FastAPI backend with health, question, feedback, debrief endpoints
- [x] Claude integration for Socratic tutoring
- [x] Eleven Labs TTS backend integration
- [x] WebSocket endpoint for real-time messaging
- [x] PatientContext alignment (widget camelCase <-> backend snake_case)
- [x] React widget package (`@meded/echo-widget`)
- [x] Widget text chat functionality
- [x] JSON response cleanup (no markdown code blocks)
- [x] Prompts exported to reviewable markdown
- [x] **Prompt overhaul** - New teaching-focused prompts based on expert interview
  - `src/prompts/system.md` - Core identity, "A teacher is a helper"
  - `src/prompts/feedback.md` - Feedback prompt reference
  - `src/prompts/question.md` - Question prompt reference
  - `src/prompts/debrief.md` - Debrief prompt reference
  - `prompts/ECHO_PROMPTS.md` - Updated reference documentation

## In Progress

- [ ] **Voice features paused** - TTS commented out in widget, marked for later

## Pending

### Priority 1 - Core Features
- [ ] Deepgram/Whisper STT integration for voice input
- [ ] Re-enable widget TTS when ready
- [ ] Test with Oread integration (end-to-end)

### Priority 2 - Polish
- [x] Error handling improvements in widget
  - User-friendly error messages (network, timeout, server errors)
  - Error banner with dismiss/retry buttons
  - Failed message indicator with retry option
- [x] Loading states and animations
  - "Echo is thinking" typing indicator
  - Send button spinner during loading
  - Smooth message slide-in animations
  - Error shake animation

### Priority 3 - Future
- [ ] Different voices for different tutor modes
- [ ] Server-side conversation history
- [ ] Integration with Syrinx and Mneme

## Notes

### Widget Embed Code
```html
<script type="module">
  import { EchoWidget } from 'https://your-cdn.com/echo-widget.js';
  // or from npm: import { EchoWidget } from '@meded/echo-widget';
</script>
```

### Quick Test Commands
```bash
# Start backend
cd /Users/dochobbs/Downloads/Consult/MedEd/echo
source ~/.zshrc && source .venv/bin/activate
uvicorn src.main:app --port 8002

# Start widget dev
cd widget && npm run dev

# Test API
curl -s http://localhost:8002/health
curl -X POST http://localhost:8002/question \
  -H "Content-Type: application/json" \
  -d '{"learner_question":"What should I ask?","learner_level":"student"}'
```
