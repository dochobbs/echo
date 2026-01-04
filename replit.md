# Echo - AI Attending Tutor for Medical Education

## Overview
Echo is an AI-powered attending tutor for medical education. It provides personalized feedback, case-based learning, and voice interactions for medical students and residents.

## Project Architecture

### Backend (Python FastAPI)
- **Location**: `src/`
- **Port**: 8001 (localhost)
- **Main entry**: `src/main.py`
- **Configuration**: `src/config.py`
- **Framework**: FastAPI with uvicorn

Key modules:
- `src/auth/` - Authentication with Supabase
- `src/cases/` - Case generation and history
- `src/cds/` - Clinical decision support (dosing, guidelines)
- `src/core/` - Core tutor functionality, citations, voice
- `src/routers/` - API endpoints (feedback, question, debrief, voice)
- `src/prompts/` - LLM prompt templates

### Frontend (React + Vite + TypeScript)
- **Location**: `web/`
- **Port**: 5000 (0.0.0.0)
- **Framework**: React 18 with Vite, TailwindCSS, React Router

Key components:
- `web/src/pages/` - Main pages (Home, Case, Login, Profile, etc.)
- `web/src/components/` - Reusable components
- `web/src/hooks/` - Custom hooks (useAuth, useCase)
- `web/src/api/` - API client and Supabase integration

### Widget Library
- **Location**: `widget/`
- Embeddable widget for external integration

### Knowledge Base
- **Location**: `knowledge/conditions/` - YAML files with medical condition data
- Covers pediatric conditions: asthma, bronchiolitis, croup, UTI, etc.

## Environment Variables Required
- `ANTHROPIC_API_KEY` - Claude API for LLM features
- `ELEVEN_API_KEY` - ElevenLabs for voice synthesis
- `DEEPGRAM_API_KEY` - Deepgram for speech-to-text
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anonymous key
- `SUPABASE_SERVICE_KEY` - Supabase service key (admin operations)

## Development
- Frontend runs on port 5000 with proxy to backend on port 8000
- Frontend: `cd web && npm run dev`
- Backend: `python -m uvicorn src.main:app --host localhost --port 8000`

## Authentication & Persistence
The backend supports optional Supabase authentication. When configured:
- Users can register/login via `/auth/register` and `/auth/login`
- Case sessions are persisted to Supabase `case_sessions` table
- Messages are saved to `messages` table
- User history is available via `/case/history` endpoint
- Active cases available via `/case/me/active` (requires auth)

Without Supabase configured, the app works with in-memory storage per session.

## API Endpoints
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login with email/password
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user profile
- `POST /case/start` - Start a new case
- `POST /case/message` - Send message in active case
- `POST /case/debrief` - Get case debrief
- `GET /case/history` - Get user's case history
- `GET /case/me/active` - Get active cases (requires auth)

## Recent Changes
- 2026-01-04: Configured for Replit environment
  - Set frontend to port 5000 with allowedHosts enabled for Replit proxy
  - Backend runs on port 8000
  - Installed Python and Node.js dependencies
- 2026-01-04: Added user authentication and case persistence
  - Wired auth router into FastAPI app
  - Created CasePersistence service for Supabase storage
  - Updated case router endpoints to save/load from database
  - Added authenticated history endpoints
