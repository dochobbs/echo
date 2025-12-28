"""Echo configuration."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
  """Application settings from environment."""

  # API Keys
  anthropic_api_key: str = ""
  eleven_labs_api_key: str = ""
  deepgram_api_key: str = ""

  # Eleven Labs
  echo_voice_id: str = ""

  # Claude
  claude_model: str = "claude-sonnet-4-20250514"

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
