# Echo Project Worklist

**Last Updated:** 2026-01-03

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
  - Vite + React + TypeScript + Tailwind CSS 4
  - Home page with "Start a case" button
  - Case chat interface
  - Responsive mobile design
- [x] Port AOM condition from Oread (`knowledge/conditions/otitis_media.yaml`)
  - Teaching goals, common mistakes, parent styles
  - Clinical details (symptoms, vitals, exam findings)
- [x] Case generation module (`src/cases/`)
  - Patient generator from condition YAML
  - CaseState model with phase tracking
  - `/case/start`, `/case/message`, `/case/debrief` endpoints
- [x] Fluid voice tutor implementation
  - Parent roleplay + teaching voice
  - Automatic phase transitions (intro → history → exam → assessment → plan)
  - Context-aware responses based on phase

---

## In Progress

### Sprint 1: Complete ✅
All Sprint 1 "Magic Moment" tasks are done:
- [x] Mobile-first web app (Vite + React + TypeScript + Tailwind CSS 4)
- [x] Zero-friction home page with "Start a case" button
- [x] Case chat interface with fluid voice tutor
- [x] AOM condition ported from Oread with teaching enhancements
- [x] TTS available (off by default, toggle in header)
- [x] localStorage persistence (resume interrupted sessions)
- [x] Complete case flow tested: intro → history → exam → assessment → plan → debrief

---

## Pending

### Sprint 2: Voice + Depth
- [ ] STT (Deepgram) - learners can speak to Echo
- [x] Expand conditions (5-10 from Oread) - **11 conditions implemented**
- [x] Stuck detection + natural hint offering - **Detects short/confused responses, offers supportive guidance**
- [x] CDS validation (dosing, guidelines) - **CDS module created with 15+ medications**
- [x] Debrief experience refinement - **DebriefCard component with structured display**

### Sprint 3: Identity + Persistence
- [x] Supabase setup - **Schema created, client ready, works in guest mode**
- [x] Email auth (optional for users) - **Auth module created (src/auth/)**
- [ ] Server-side case storage
- [ ] Cross-device case resume

### Sprint 4: Memory + Personalization
- [ ] Case history tracking per user
- [ ] Return-visit greetings ("Good to see you! Last time we did respiratory...")
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
│   │   ├── generator.py    # Patient generation from YAML
│   │   ├── models.py       # CaseState, GeneratedPatient
│   │   └── router.py       # /case/* endpoints
│   ├── routers/            # Other API routes
│   └── prompts/            # System, feedback, question, debrief prompts
├── knowledge/
│   └── conditions/         # Condition YAML files
│       └── otitis_media.yaml
├── web/                    # Standalone web app
│   ├── src/
│   │   ├── pages/          # Home, Case
│   │   └── types/          # TypeScript types
│   └── package.json
└── widget/                 # Embeddable widget (for Oread/etc)
```
