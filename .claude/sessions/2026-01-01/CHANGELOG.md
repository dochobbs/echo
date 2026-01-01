# Changelog - 2026-01-01

## Features

- `7c0e151`: FEATURE: Add WebSocket, fix JSON responses, align PatientContext
  - WebSocket endpoint at `/voice/conversation`
  - `clean_json_response()` helper for JSON cleanup
  - `WidgetPatientContext` for camelCase format support
  - Config updated for `ELEVEN_API_KEY` env var
  - Widget voice features commented out (TODO)
  - Lucide icons replacing emojis
  - Node_modules added to gitignore

## Documentation

- `4f771ec`: DOCS: Add Echo prompts reference file
  - All tutor prompts exported to `prompts/ECHO_PROMPTS.md`
  - System prompt, feedback, question, debrief documented
  - Variable reference table included

## Previous Session Commits (for context)

- `7759361`: FEATURE: Add cyan MessageCircle icon favicon and demo page
- `6dbcdb1`: FEATURE: Add React widget package for embedding Echo
- `7d3d9f2`: FEATURE: Add Eleven Labs TTS integration
- `8c560b2`: Initial Echo scaffold
