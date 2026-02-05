# Echo Project Worklist

**Last Updated:** 2026-02-04

## Vision

**The best attending in your pocket** - infinitely patient, brilliant, and kind.

Target: Medical learner with 30 minutes at lunch wanting to run a case.

---

## Completed

### Core Infrastructure
- [x] Git repo setup and initial scaffold
- [x] FastAPI backend with health, question, feedback, debrief endpoints
- [x] Claude integration for Socratic tutoring
- [x] Eleven Labs TTS backend integration
- [x] WebSocket endpoint for real-time messaging

### Widget (for Oread/Syrinx/Mneme embed)
- [x] React widget package (`@meded/echo-widget`)
- [x] Widget text chat functionality
- [x] Error handling improvements (user-friendly messages, retry)
- [x] Loading states and animations ("Echo is thinking", slide-in)

### Prompt Engineering
- [x] **Prompt overhaul** - Expert interview-based teaching prompts
  - `src/prompts/system.md` - Core identity: "A teacher is a helper"
  - Feedback, question, debrief prompts
  - Fluid voice switching (roleplay + teaching seamlessly)

### Sprint 1: The Magic Moment ✅ COMPLETE
- [x] Mobile-first web app scaffold (`web/` directory)
- [x] Port AOM condition from Oread
- [x] Case generation module (`src/cases/`)
- [x] Fluid voice tutor implementation
- [x] TTS available (off by default, toggle in header)
- [x] localStorage persistence

### Sprint 2: Voice + Depth ✅ MOSTLY COMPLETE
- [x] Expand conditions to 11
- [x] Stuck detection + natural hint offering
- [x] CDS validation (dosing, guidelines)
- [x] Debrief experience refinement
- [ ] STT (Deepgram) - learners can speak to Echo

### Teaching Frameworks ✅ NEW - 2026-01-04
- [x] **100 condition teaching frameworks** - Full pediatric curriculum coverage
- [x] Framework schema with teaching fields (goals, mistakes, pearls, red flags)
- [x] Framework loader module (`src/knowledge/framework_loader.py`)
- [x] Replit deployment bundle (`frameworks_bundle.tar.gz`)

### Licensing ✅ 2026-01-20
- [x] Added AGPL-3.0 license (copyleft, covers network use)
- [x] Copyright: Michael Hobbs <michael@hobbs.md>

---

## Ready for Replit Integration

### Files to Upload
- `frameworks_bundle.tar.gz` (106 KB) - Everything bundled
- `REPLIT_HANDOFF.md` - Integration instructions

### Integration Tasks
- [ ] Upload and extract frameworks bundle
- [ ] Add `/frameworks` API endpoints
- [ ] Update case generation to use framework teaching context
- [ ] Add condition selector UI

---

## Pending

### Auth Bug Fix (2026-02-04)
- [x] Fix: ApiClient.fetch() not loading stored JWT after page refresh
  - Learners could not access old cases after refresh/return visit
  - Root cause: `ensureInitialized()` missing from `fetch()` method

### Sprint 3: Identity + Persistence
- [x] Supabase setup - Schema created, client ready
- [x] Auth module structure - `src/auth/`
- [x] Server-side case storage
- [ ] Cross-device case resume (partially fixed - auth token now persists)
- [ ] Harden case history endpoints (require auth, remove in-memory fallback)
- [ ] Fix in-memory history user isolation (no user filtering when DB is down)

### Sprint 4: Memory + Personalization
- [ ] Case history tracking per user
- [ ] Return-visit greetings
- [ ] Adaptive case selection
- [ ] Time constraint check-ins

### Sprint 5: Competency Tracking
- [ ] Competency framework (ACGME/AAP based)
- [ ] Progress display (natural language, not gamification)

### Sprint 6: Admin + Polish
- [ ] Admin dashboard
- [ ] Usage metrics
- [ ] Performance optimization

---

## Quick Start

### Backend
```bash
cd /Users/dochobbs/Downloads/Consult/MedEd/echo
source .venv/bin/activate
uvicorn src.main:app --port 8002
```

### Web App
```bash
cd web
npm run dev  # http://localhost:3001
```

### Test Case Endpoint
```bash
curl -X POST http://localhost:8002/case/start \
  -H "Content-Type: application/json" \
  -d '{"learner_level": "student"}'
```

---

## Architecture

```
echo/
├── src/                    # Backend
│   ├── main.py             # FastAPI app
│   ├── core/tutor.py       # Claude-based tutor with fluid voice
│   ├── cases/              # Case generation
│   ├── knowledge/          # NEW: Framework loader
│   │   └── framework_loader.py
│   ├── routers/            # API routes
│   └── prompts/            # System, feedback, question, debrief prompts
├── knowledge/
│   ├── conditions/         # Full condition YAML files
│   └── frameworks/         # NEW: 100 teaching frameworks
├── web/                    # Standalone web app
└── widget/                 # Embeddable widget
```

---

## Framework Categories (100 total)

| Category | Count |
|----------|-------|
| Newborn/Infant | 15 |
| Infectious Disease | 17 |
| Respiratory/Allergy | 5 |
| Dermatology | 11 |
| Behavioral/Developmental | 12 |
| GI | 6 |
| Emergency/Trauma | 10 |
| MSK | 6 |
| Endocrine | 7 |
| Nephrology/Urology | 7 |
| Hematology/Oncology | 2 |
| Adolescent/GYN | 3 |
