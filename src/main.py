"""Echo - AI Attending Tutor Service."""

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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
  """Initialize database tables on startup."""
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
