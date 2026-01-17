# Echo - AI Attending Tutor for Medical Education

## Overview
Echo is an AI-powered attending tutor for medical education. It provides personalized feedback, case-based learning, and voice interactions for medical students and residents.

## Project Architecture

### Backend (Python FastAPI)
- **Location**: `src/`
- **Port**: 8000 (localhost)
- **Main entry**: `src/main.py`
- **Configuration**: `src/config.py`
- **Framework**: FastAPI with uvicorn

Key modules:
- `src/auth/` - Authentication with local JWT tokens
- `src/cases/` - Case generation, history, and dynamic case variants
- `src/cds/` - Clinical decision support (dosing, guidelines)
- `src/core/` - Core tutor functionality, citations, voice
- `src/routers/` - API endpoints (feedback, question, debrief, voice)
- `src/prompts/` - LLM prompt templates
- `src/database.py` - SQLAlchemy database connection
- `src/db_models.py` - SQLAlchemy ORM models (User, CaseSession, Message)
- `src/admin/` - Admin dashboard and management endpoints
- `src/patients/` - Patient import (CCDA parser) and management
- `src/knowledge/` - Framework loader for teaching frameworks

### Frontend (React + Vite + TypeScript)
- **Location**: `web/`
- **Port**: 5000 (0.0.0.0)
- **Framework**: React 18 with Vite, TailwindCSS, React Router

Key components:
- `web/src/pages/` - Main pages (Home, Case, Login, Profile, etc.)
- `web/src/components/` - Reusable components
- `web/src/hooks/` - Custom hooks (useAuth, useCase)
- `web/src/api/` - API client

### Widget Library
- **Location**: `widget/`
- Embeddable widget for external integration

### Knowledge Base
- **Location**: `knowledge/conditions/` - YAML files with patient generation data (demographics, symptoms, vitals)
- **Location**: `knowledge/frameworks/` - 100 YAML teaching frameworks with learning objectives
- Covers full pediatric curriculum: infectious, respiratory, GI, derm, behavioral, emergency, etc.

### Teaching Frameworks Module
- **Location**: `src/frameworks/`
- **Loader**: `src/frameworks/loader.py` - Loads and queries 100 teaching frameworks
- **Router**: `src/frameworks/router.py` - API endpoints for framework access
- Each framework includes: teaching_goals, common_mistakes, red_flags, clinical_pearls, key_history_questions, key_exam_findings, treatment_principles

## Database Schema (PostgreSQL)
Uses Replit's built-in PostgreSQL database with SQLAlchemy ORM.

**Tables:**
- `users` - User accounts with email, password hash, profile info
- `case_sessions` - Case session data with patient info, progress, status
- `messages` - Conversation messages for each case session

## Environment Variables Required
- `DATABASE_URL` - PostgreSQL connection (auto-configured by Replit)
- `JWT_SECRET` - Secret for JWT token signing (optional, has default)
- `ANTHROPIC_API_KEY` - Claude API for LLM features
- `ELEVEN_API_KEY` - ElevenLabs for voice synthesis
- `DEEPGRAM_API_KEY` - Deepgram for speech-to-text

## Development
- Frontend runs on port 5000 with proxy to backend on port 8000
- Frontend: `cd web && npm run dev`
- Backend: `python -m uvicorn src.main:app --host localhost --port 8000 --reload`
- Database tables are auto-created on backend startup

## Authentication & Persistence
The backend uses local JWT authentication with PostgreSQL storage:
- Users can register/login via `/auth/register` and `/auth/login`
- Access tokens expire in 24 hours, refresh tokens in 7 days
- Case sessions are persisted to `case_sessions` table
- Messages are saved to `messages` table
- User history is available via `/case/history` endpoint
- Active cases available via `/case/me/active` (requires auth)

Without DATABASE_URL configured, the app works with in-memory storage per session.

## API Endpoints
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login with email/password
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Get current user profile
- `PATCH /auth/me` - Update user profile
- `GET /auth/me/stats` - Get user case statistics
- `POST /case/start` - Start a new case
- `POST /case/message` - Send message in active case
- `POST /case/debrief` - Get case debrief
- `GET /case/history` - Get user's case history
- `GET /case/me/active` - Get active cases (requires auth)
- `GET /frameworks` - List all 100 teaching frameworks
- `GET /frameworks/{key}` - Get specific framework by key
- `GET /frameworks/categories` - List all categories with counts
- `GET /frameworks/category/{category}` - Get frameworks in category

## Design System
The app uses a "Clinical Calm" dark theme with Geist Mono font:

**Colors:**
- Primary: Echo teal (`#0D9CB8`)
- Accent: Copper (`#E07B54`)
- Surfaces: Dark grays (`#0a0a0b` to `#27272a`)

**Typography:**
- Font: Geist Mono (loaded from jsDelivr CDN)
- Monospace styling throughout for technical aesthetic

**Components:**
- `FocusTextarea` - Text input with screen fade focus effect
- `CaseTimeline` - Animated phase progress indicator
- `TypingIndicator` - Animated dots for AI thinking state
- `MessageBubble` - Animated chat messages with slide-in effect
- `MobileNav` - Bottom tab bar for mobile navigation
- `Toast` - Notification toasts for milestones

## Recent Changes
- 2026-01-17: Incorporated major platform updates
  - Added 25 new pediatric teaching frameworks (now 125 total)
  - Added admin dashboard module (`src/admin/`)
  - Added patient import with CCDA parser (`src/patients/`)
  - Added dynamic case variants generator
  - Enhanced debrief with Q&A capability
  - Improved tutor prompt with framework integration
- 2026-01-17: Fixed case resumption and describe feature
  - Users can now resume active cases from history page
  - "Describe a Case" properly sends initial description
  - Added error handling for failed case loads
- 2026-01-04: Integrated 100 teaching frameworks for dynamic case generation
  - Added knowledge/frameworks/ with full pediatric curriculum YAML files
  - Created src/frameworks/ module with loader and API router
  - Frameworks provide teaching_goals, common_mistakes, red_flags, clinical_pearls
  - Case generator now merges framework data with patient generation
  - Tutor prompts enhanced with key questions, exam findings, treatment principles
- 2026-01-04: Fixed History page crash - updated to match backend API response format (patient_name, patient_age fields)
- 2026-01-04: FocusTextarea now auto-grows as users type new lines (min 56px, max 300px)
- 2026-01-04: Fixed authentication and replaced emojis with animated icons
  - Rewired useAuth hook to use local JWT endpoints (/auth/login, /auth/register)
  - Added SSR-safe localStorage handling in API client
  - Created animated icon components based on itshover.com style
  - Replaced all emoji icons with motion-animated SVG icons
  - Icons: HomeIcon, UserIcon, HistoryIcon, SendIcon, SpinnerIcon, etc.
- 2026-01-04: Major UI redesign with Geist Mono font
  - Dark theme with teal/copper accent colors
  - Added animated components (timeline, typing indicator, message bubbles)
  - Focus-mode text box with screen fade overlay
  - Mobile-first navigation with bottom tab bar
  - Framer Motion animations throughout
- 2026-01-04: Migrated from Supabase to Replit PostgreSQL
  - Created SQLAlchemy models (User, CaseSession, Message)
  - Implemented local JWT authentication (bcrypt + PyJWT)
  - Updated persistence layer to use SQLAlchemy
  - Database tables auto-created on startup
  - Removed Supabase dependencies from auth and persistence
- 2026-01-04: Configured for Replit environment
  - Set frontend to port 5000 with allowedHosts enabled for Replit proxy
  - Backend runs on port 8000
  - Installed Python and Node.js dependencies
