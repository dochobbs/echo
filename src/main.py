"""Echo - AI Attending Tutor Service."""

import os
from pathlib import Path

import anthropic
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .routers import feedback, question, debrief, voice
from .cases import case_router
from .auth.router import router as auth_router
from .admin.router import router as admin_router
from .patients.router import router as patients_router
from .frameworks.router import router as frameworks_router
from .database import is_database_configured, create_tables

app = FastAPI(
  title="Echo",
  description="AI Attending Tutor for Medical Education",
  version="0.1.0",
)


# --- Global Anthropic error handler ---
# Stop leaking SDK exceptions to clients as opaque 500s. Translate rate-limit,
# auth, and connection failures into structured JSON the portal can render.
@app.exception_handler(anthropic.APIStatusError)
async def _anthropic_status_handler(request: Request, exc: anthropic.APIStatusError):
  status_code = getattr(exc, "status_code", 502)
  retry_after = None
  try:
    retry_after = int(exc.response.headers.get("retry-after", 0)) or None
  except Exception:
    pass
  return JSONResponse(
    status_code=status_code if 400 <= status_code < 600 else 502,
    content={
      "error": "claude_api_error",
      "message": str(exc),
      "retry_after": retry_after,
    },
  )


@app.exception_handler(anthropic.APIConnectionError)
async def _anthropic_conn_handler(request: Request, exc: anthropic.APIConnectionError):
  return JSONResponse(
    status_code=503,
    content={
      "error": "claude_api_unavailable",
      "message": "Cannot reach Anthropic API; check network or service status.",
      "retry_after": 30,
    },
  )

# CORS for web clients
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(patients_router)
app.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
app.include_router(question.router, prefix="/question", tags=["question"])
app.include_router(debrief.router, prefix="/debrief", tags=["debrief"])
app.include_router(voice.router, prefix="/voice", tags=["voice"])
app.include_router(case_router, tags=["cases"])
app.include_router(frameworks_router)


@app.on_event("startup")
async def startup():
  """Validate required config and initialize database tables on startup."""
  import sys

  # Required: Claude API for tutoring
  settings = get_settings()
  if not settings.anthropic_api_key:
    print(
      "FATAL: ANTHROPIC_API_KEY not set. Echo requires Claude API for tutoring. "
      "Set the env var and restart.",
      file=sys.stderr,
    )
    sys.exit(1)

  # Optional: voice. Warn but don't fail.
  if not settings.eleven_api_key:
    print(
      "WARN: ELEVEN_LABS_API_KEY not set. /voice/speak will return 501 if invoked.",
      file=sys.stderr,
    )
  if not getattr(settings, "deepgram_api_key", None):
    print(
      "WARN: DEEPGRAM_API_KEY not set. Voice STT will fall back to local Whisper.",
      file=sys.stderr,
    )

  if is_database_configured():
    create_tables()
    print("Database tables created/verified.")
  else:
    print("Database not configured - running without persistence.")


STATIC_DIR = Path(__file__).parent.parent / "web" / "dist"

@app.get("/")
async def root():
  """Root endpoint - serve frontend in production, API info in dev."""
  if STATIC_DIR.exists() and (STATIC_DIR / "index.html").exists():
    return FileResponse(STATIC_DIR / "index.html")
  return {
    "service": "Echo",
    "version": "0.1.0",
    "description": "AI Attending Tutor",
  }


@app.get("/health")
async def health():
  """Health check."""
  settings = get_settings()
  db_configured = is_database_configured()
  return {
    "status": "healthy",
    "claude_configured": bool(settings.anthropic_api_key),
    "eleven_labs_configured": bool(settings.eleven_api_key),
    "database_configured": db_configured,
    "auth_enabled": db_configured,
  }


# Serve static frontend files in production
if STATIC_DIR.exists():
  # Mount assets directory for static files (JS, CSS, images)
  assets_dir = STATIC_DIR / "assets"
  if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
  
  @app.get("/{full_path:path}")
  async def serve_spa(request: Request, full_path: str):
    """Serve the SPA for all non-API routes."""
    # Check if requesting a static file
    file_path = STATIC_DIR / full_path
    if file_path.is_file():
      return FileResponse(file_path)
    # Otherwise return index.html for SPA routing
    return FileResponse(STATIC_DIR / "index.html")


if __name__ == "__main__":
  import uvicorn
  settings = get_settings()
  uvicorn.run(app, host=settings.echo_host, port=settings.echo_port)
