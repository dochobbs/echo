"""Echo configuration."""

from pydantic_settings import BaseSettings
from functools import lru_cache


# Available Echo voices (Eleven Labs)
ECHO_VOICES: dict[str, str] = {
  "eryn": "WuBPEavIaQB56EnsGvFh",      # Default - calm, confident
  "matilda": "NihRgaLj2HWAjvZ5XNxl",   # Warm, friendly
  "clarice": "sIak7pFapfSLCfctxdOu",   # Clear, professional
  "clara": "Qggl4b0xRMiqOwhPtVWT",     # Approachable
  "devan": "mC104ON19u9NruNfYC3j",     # Energetic
  "lilly": "qBDvhofpxp92JgXJxDjB",     # Gentle
}

DEFAULT_VOICE = "eryn"


class Settings(BaseSettings):
  """Application settings from environment."""

  # API Keys
  anthropic_api_key: str = ""
  eleven_api_key: str = ""  # Maps to ELEVEN_API_KEY env var
  deepgram_api_key: str = ""
  exa_api_key: str = ""  # For medical citations

  # Supabase
  supabase_url: str = ""
  supabase_anon_key: str = ""
  supabase_service_key: str = ""  # For admin operations
  jwt_secret: str = ""  # For signing JWTs

  # Eleven Labs
  echo_voice_id: str = ECHO_VOICES[DEFAULT_VOICE]
  eleven_labs_model: str = "eleven_multilingual_v2"

  # Claude
  claude_model: str = "claude-sonnet-4-5-20250929"

  # Server
  echo_host: str = "0.0.0.0"
  echo_port: int = 8001

  class Config:
    env_file = ".env"
    env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
  """Get cached settings instance."""
  return Settings()
