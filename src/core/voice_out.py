"""Eleven Labs TTS integration for Echo voice output."""

from typing import AsyncIterator, Optional
import io

from elevenlabs import AsyncElevenLabs
from elevenlabs.types import VoiceSettings

from src.config import get_settings, ECHO_VOICES, DEFAULT_VOICE


class VoiceOut:
  """Eleven Labs text-to-speech service."""

  def __init__(self):
    settings = get_settings()
    self.client = AsyncElevenLabs(api_key=settings.eleven_labs_api_key)
    self.model_id = settings.eleven_labs_model
    self.default_voice_id = settings.echo_voice_id

  async def synthesize(
    self,
    text: str,
    voice: Optional[str] = None,
    output_format: str = "mp3_44100_128",
  ) -> bytes:
    """Convert text to speech audio bytes.

    Args:
      text: The text to convert to speech.
      voice: Voice name (eryn, matilda, etc.) or voice ID. Defaults to Eryn.
      output_format: Audio format. Options: mp3_44100_128, pcm_16000, etc.

    Returns:
      Audio bytes in the specified format.
    """
    voice_id = self._resolve_voice_id(voice)

    audio_generator = await self.client.text_to_speech.convert(
      text=text,
      voice_id=voice_id,
      model_id=self.model_id,
      output_format=output_format,
      voice_settings=VoiceSettings(
        stability=0.5,
        similarity_boost=0.75,
        style=0.0,
        use_speaker_boost=True,
      ),
    )

    # Collect all chunks into bytes
    chunks = []
    async for chunk in audio_generator:
      if isinstance(chunk, bytes):
        chunks.append(chunk)

    return b"".join(chunks)

  async def stream(
    self,
    text: str,
    voice: Optional[str] = None,
    output_format: str = "mp3_44100_128",
  ) -> AsyncIterator[bytes]:
    """Stream text-to-speech audio chunks.

    Args:
      text: The text to convert to speech.
      voice: Voice name or ID. Defaults to Eryn.
      output_format: Audio format.

    Yields:
      Audio chunks as bytes.
    """
    voice_id = self._resolve_voice_id(voice)

    audio_stream = await self.client.text_to_speech.convert(
      text=text,
      voice_id=voice_id,
      model_id=self.model_id,
      output_format=output_format,
      voice_settings=VoiceSettings(
        stability=0.5,
        similarity_boost=0.75,
        style=0.0,
        use_speaker_boost=True,
      ),
    )

    async for chunk in audio_stream:
      if isinstance(chunk, bytes):
        yield chunk

  def _resolve_voice_id(self, voice: Optional[str]) -> str:
    """Resolve voice name to Eleven Labs voice ID."""
    if voice is None:
      return self.default_voice_id

    # Check if it's a voice name we know
    voice_lower = voice.lower()
    if voice_lower in ECHO_VOICES:
      return ECHO_VOICES[voice_lower]

    # Assume it's already a voice ID
    return voice

  @staticmethod
  def list_voices() -> dict[str, str]:
    """Return available Echo voices."""
    return ECHO_VOICES.copy()

  @staticmethod
  def get_default_voice() -> str:
    """Return the default voice name."""
    return DEFAULT_VOICE


# Singleton instance
_voice_out: Optional[VoiceOut] = None


def get_voice_out() -> VoiceOut:
  """Get or create the VoiceOut singleton."""
  global _voice_out
  if _voice_out is None:
    _voice_out = VoiceOut()
  return _voice_out
