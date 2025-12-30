"""Voice endpoints - TTS for Echo responses and real-time conversation."""

import json
import base64
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..core.voice_out import VoiceOut, get_voice_out
from ..core.tutor import get_tutor
from ..models.feedback import QuestionRequest
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


@router.websocket("/conversation")
async def conversation_websocket(websocket: WebSocket):
  """
  Real-time conversation WebSocket endpoint.

  Accepts JSON messages with the following format:
  {
    "type": "message",
    "text": "learner's question or statement",
    "learner_level": "student",  // optional
    "voice": "eryn",             // optional, for TTS
    "include_audio": false       // optional, include TTS audio in response
  }

  Responds with:
  {
    "type": "response",
    "text": "Echo's response",
    "topic": "clinical concept",
    "hint": "optional hint",
    "audio": "base64-encoded-mp3"  // if include_audio was true
  }
  """
  await websocket.accept()

  tutor = get_tutor()
  voice_out = get_voice_out()

  try:
    while True:
      # Receive message from client
      data = await websocket.receive_text()

      try:
        message = json.loads(data)
      except json.JSONDecodeError:
        await websocket.send_json({
          "type": "error",
          "message": "Invalid JSON format",
        })
        continue

      if message.get("type") == "ping":
        await websocket.send_json({"type": "pong"})
        continue

      if message.get("type") != "message":
        await websocket.send_json({
          "type": "error",
          "message": f"Unknown message type: {message.get('type')}",
        })
        continue

      text = message.get("text", "").strip()
      if not text:
        await websocket.send_json({
          "type": "error",
          "message": "Message text cannot be empty",
        })
        continue

      # Process with tutor
      try:
        request = QuestionRequest(
          learner_question=text,
          learner_level=message.get("learner_level", "student"),
        )
        response = await tutor.ask_socratic_question(request)

        result = {
          "type": "response",
          "text": response.question,
          "topic": response.topic,
          "hint": response.hint,
        }

        # Include TTS audio if requested
        if message.get("include_audio", False):
          voice = message.get("voice", DEFAULT_VOICE)
          audio_bytes = await voice_out.synthesize(
            text=response.question,
            voice=voice,
          )
          result["audio"] = base64.b64encode(audio_bytes).decode("utf-8")

        await websocket.send_json(result)

      except Exception as e:
        await websocket.send_json({
          "type": "error",
          "message": f"Tutor error: {str(e)}",
        })

  except WebSocketDisconnect:
    pass  # Client disconnected normally
