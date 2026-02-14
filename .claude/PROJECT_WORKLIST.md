# Echo Project Worklist

**Last Updated:** 2026-02-12

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

### Sprint 1: The Magic Moment
- [x] Mobile-first web app scaffold (`web/` directory)
- [x] Port AOM condition from Oread
- [x] Case generation module (`src/cases/`)
- [x] Fluid voice tutor implementation
- [x] TTS available (off by default, toggle in header)
- [x] localStorage persistence

### Sprint 2: Voice + Depth
- [x] Expand conditions to 11
- [x] Stuck detection + natural hint offering
- [x] CDS validation (dosing, guidelines)
- [x] Debrief experience refinement

### Teaching Frameworks
- [x] **100 condition teaching frameworks** - Full pediatric curriculum coverage
- [x] Framework schema with teaching fields (goals, mistakes, pearls, red flags)
- [x] Framework loader module (`src/knowledge/framework_loader.py`)

### Licensing
- [x] Added AGPL-3.0 license (copyleft, covers network use)

### Auth
- [x] Fix: ApiClient.fetch() not loading stored JWT after page refresh
- [x] Supabase setup - Schema created, client ready
- [x] Auth module structure - `src/auth/`
- [x] Server-side case storage

### Well-Child Visits (2026-02-12) - NEW
- [x] 13 AAP Bright Futures well-child frameworks (newborn through adolescent)
- [x] Well-child framework schema with growth data, milestones, immunizations, guidance
- [x] WellChildGenerator with incidental finding support and probability weights
- [x] Framework loader methods for well-child filtering
- [x] Tutor well-child prompt and debrief prompt templates
- [x] Tutor well-child phase detection, system prompt building, 6-domain debrief scoring
- [x] API routing for well-child cases through `/start`, `/message`, `/debrief`
- [x] Database columns for well-child tracking (visit_type, visit_age_months, etc.)
- [x] Frontend: visit type selector (Sick/Well-Child), age picker grid
- [x] Frontend: well-child phase timeline with emerald color theme
- [x] Frontend: domain score cards in DebriefCard component
- [x] TypeScript types and API client updates for well-child support

---

## Pending

### Well-Child Follow-Up
- [ ] End-to-end testing of all 13 visit ages with Claude API
- [ ] Verify debrief scoring produces meaningful domain-level feedback
- [ ] Save well-child tracking fields to database (growth_reviewed, milestones_assessed, etc.)
- [ ] Well-child admin views for case review

### Sprint 2 Remaining
- [ ] STT (Deepgram) - learners can speak to Echo

### Sprint 3: Identity + Persistence
- [ ] Cross-device case resume
- [ ] Harden case history endpoints (require auth, remove in-memory fallback)
- [ ] Fix in-memory history user isolation

### Sprint 4: Memory + Personalization
- [ ] Case history tracking per user
- [ ] Return-visit greetings
- [ ] Adaptive case selection
- [ ] Time constraint check-ins

### Sprint 5: Competency Tracking
- [ ] Competency framework (ACGME/AAP based)
- [ ] Progress display (natural language, not gamification)

### Sprint 6: Admin + Polish
- [ ] Admin dashboard enhancements
- [ ] Usage metrics
- [ ] Performance optimization

---

## Quick Start

### Backend
```bash
cd /Users/dochobbs/Downloads/Consult/MedEd/echo
source .venv/bin/activate
uvicorn src.main:app --port 8001
```

### Web App
```bash
cd web
npm run dev  # http://localhost:5000
```

### Test Well-Child Case
```bash
curl -X POST http://localhost:8001/case/start \
  -H "Content-Type: application/json" \
  -d '{"learner_level": "student", "visit_type": "well_child", "visit_age_months": 12}'
```

---

## Architecture

```
echo/
├── src/
│   ├── main.py             # FastAPI app
│   ├── core/tutor.py       # Claude tutor (sick + well-child)
│   ├── cases/
│   │   ├── models.py       # VisitType, CasePhase, WellChildScores
│   │   ├── router.py       # /start, /message, /debrief
│   │   └── well_child_generator.py  # NEW
│   ├── frameworks/
│   │   └── loader.py       # Framework + well-child loader
│   └── prompts/
│       ├── well_child.md        # NEW: Well-child teaching prompt
│       └── well_child_debrief.md # NEW: 6-domain scoring rubric
├── knowledge/
│   └── frameworks/
│       ├── _well_child_schema.yaml  # NEW
│       └── well_child_*.yaml        # NEW: 13 visit-age frameworks
├── web/                    # React frontend
├── tests/                  # 20 tests passing
└── widget/                 # Embeddable widget
```

## Framework Categories

| Category | Count |
|----------|-------|
| Sick Visit (conditions) | 100 |
| Well-Child Visit (ages) | 13 |
| **Total** | **113** |
