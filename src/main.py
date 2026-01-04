"""Echo - AI Attending Tutor Service."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import feedback, question, debrief, voice
from .cases import case_router

app = FastAPI(
  title="Echo",
  description="AI Attending Tutor for Medical Education",
  version="0.1.0",
)

# CORS for web clients
app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],  # Configure for production
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# Include routers
app.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
app.include_router(question.router, prefix="/question", tags=["question"])
app.include_router(debrief.router, prefix="/debrief", tags=["debrief"])
app.include_router(voice.router, prefix="/voice", tags=["voice"])
app.include_router(case_router, tags=["cases"])


@app.get("/")
async def root():
  """Root endpoint."""
  return {
    "service": "Echo",
    "version": "0.1.0",
    "description": "AI Attending Tutor",
  }


@app.get("/health")
async def health():
  """Health check."""
  settings = get_settings()
  return {
    "status": "healthy",
    "claude_configured": bool(settings.anthropic_api_key),
    "eleven_labs_configured": bool(settings.eleven_api_key),
  }


if __name__ == "__main__":
  import uvicorn
  settings = get_settings()
  uvicorn.run(app, host=settings.echo_host, port=settings.echo_port)
