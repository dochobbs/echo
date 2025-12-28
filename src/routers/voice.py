"""Voice endpoints - TTS for Echo responses."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..core.voice_out import VoiceOut, get_voice_out
from ..config import ECHO_VOICES, DEFAULT_VOICE


router = APIRouter()


class SpeakRequest(BaseModel):
  """Request to synthesize speech."""
  text: str
  voice: Optional[str] = None  # Voice name or ID, defaults to Eryn


class VoiceInfo(BaseModel):
  """Information about an available voice."""
  name: str
  voice_id: str
  is_default: bool


@router.post("/speak")
async def speak(
  request: SpeakRequest,
  voice_out: VoiceOut = Depends(get_voice_out),
):
  """
  Convert text to speech and return audio.

  Returns MP3 audio bytes. Use voice parameter to select a voice:
  - eryn (default), matilda, clarice, clara, devan, lilly

  Example:
    POST /voice/speak
    {"text": "What findings made you consider that diagnosis?", "voice": "eryn"}
  """
  if not request.text.strip():
    raise HTTPException(status_code=400, detail="Text cannot be empty")

  try:
    audio_bytes = await voice_out.synthesize(
      text=request.text,
      voice=request.voice,
    )

    return StreamingResponse(
      iter([audio_bytes]),
      media_type="audio/mpeg",
      headers={
        "Content-Disposition": "inline; filename=echo_speech.mp3",
        "Content-Length": str(len(audio_bytes)),
      },
    )
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"TTS synthesis failed: {str(e)}")


@router.post("/speak/stream")
async def speak_stream(
  request: SpeakRequest,
  voice_out: VoiceOut = Depends(get_voice_out),
):
  """
  Stream text to speech audio chunks.

  Returns chunked MP3 audio for lower latency playback.
  """
  if not request.text.strip():
    raise HTTPException(status_code=400, detail="Text cannot be empty")

  async def audio_generator():
    try:
      async for chunk in voice_out.stream(
        text=request.text,
        voice=request.voice,
      ):
        yield chunk
    except Exception as e:
      raise HTTPException(status_code=500, detail=f"TTS stream failed: {str(e)}")

  return StreamingResponse(
    audio_generator(),
    media_type="audio/mpeg",
  )


@router.get("/voices", response_model=list[VoiceInfo])
async def list_voices():
  """
  List available Echo voices.

  Returns all configured voices with their IDs and default status.
  """
  voices = []
  for name, voice_id in ECHO_VOICES.items():
    voices.append(VoiceInfo(
      name=name.capitalize(),
      voice_id=voice_id,
      is_default=(name == DEFAULT_VOICE),
    ))
  return voices
