# Session Summary - 2026-01-01

## Project
Echo - AI Attending Tutor Service
`/Users/dochobbs/Downloads/Consult/MedEd/echo`

## Branch
main

## Accomplishments

### WebSocket & Real-time Messaging
- Added WebSocket endpoint at `/voice/conversation` for real-time tutoring
- Supports JSON messages with optional TTS audio response
- Ping/pong keepalive support

### JSON Response Fixes
- Fixed issue where Claude returned markdown code blocks in JSON responses
- Added `clean_json_response()` helper to strip formatting
- Updated all prompts to explicitly request raw JSON

### PatientContext Alignment
- Created `WidgetPatientContext` for JavaScript-friendly camelCase format
- Backend auto-detects and converts widget format to internal snake_case
- Widget can now send full patient context with API requests

### Widget Voice Features
- Commented out TTS/voice features (marked TODO for later implementation)
- Removed Listen button and voice toggle from UI
- Fixed unused import/variable TypeScript errors

### Configuration & Environment
- Updated config to use `ELEVEN_API_KEY` (matching user's env var naming)
- Fixed Eleven Labs configuration detection in health endpoint

### Documentation
- Exported all Echo prompts to `prompts/ECHO_PROMPTS.md` for review
- System prompt, feedback, question, and debrief prompts documented

## Commits Made
- `4f771ec`: DOCS: Add Echo prompts reference file
- `7c0e151`: FEATURE: Add WebSocket, fix JSON responses, align PatientContext

## Issues Encountered
- Widget was sending `encounter_state` field that didn't exist in backend (fixed)
- PatientContext format mismatch between widget (camelCase) and backend (snake_case) (fixed)
- Eleven Labs API key env var named `ELEVEN_API_KEY` not `ELEVEN_LABS_API_KEY` (fixed)
- Voice/TTS features had issues - decided to pause and implement later

## Decisions Made
- Pause voice/TTS features in widget for now (commented out with TODO markers)
- Use flexible PatientContext that accepts both widget and backend formats
- Export prompts to markdown for easier review and iteration

## Next Steps
- [ ] Implement Deepgram/Whisper STT for voice input
- [ ] Re-enable widget TTS when ready
- [ ] Test with Oread integration
- [ ] Create prompt template files (feedback.md, debrief.md)
- [ ] Push to remote (`git push`)
