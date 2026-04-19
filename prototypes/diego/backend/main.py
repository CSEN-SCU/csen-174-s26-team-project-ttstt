"""TTSTT prototype backend — STT and TTS endpoints."""

from __future__ import annotations

import io
import os
import tempfile
from pathlib import Path

import edge_tts
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from faster_whisper import WhisperModel

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL", "base")
DEFAULT_VOICE = os.getenv("TTS_VOICE", "en-US-AriaNeural")

app = FastAPI(title="TTSTT Prototype API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

whisper_model: WhisperModel | None = None


def get_whisper() -> WhisperModel:
    global whisper_model
    if whisper_model is None:
        whisper_model = WhisperModel(WHISPER_MODEL_SIZE, compute_type="int8")
    return whisper_model


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/api/stt")
async def speech_to_text(audio: UploadFile = File(...)) -> dict:
    """Accept an audio blob, return transcribed text."""
    model = get_whisper()

    suffix = ".webm"
    if audio.content_type and "wav" in audio.content_type:
        suffix = ".wav"

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(await audio.read())
        tmp_path = tmp.name

    try:
        segments, _info = model.transcribe(tmp_path, beam_size=5)
        text = " ".join(seg.text.strip() for seg in segments)
    finally:
        os.unlink(tmp_path)

    return {"text": text}


@app.post("/api/tts")
async def text_to_speech(
    text: str = Form(...),
    voice: str = Form(None),
    rate: str = Form("+0%"),
    pitch: str = Form("+0Hz"),
) -> StreamingResponse:
    """Convert text to speech audio, return MP3 bytes."""
    voice = voice or DEFAULT_VOICE

    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)

    buffer = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buffer.write(chunk["data"])

    buffer.seek(0)
    return StreamingResponse(buffer, media_type="audio/mpeg")


@app.get("/api/voices")
async def list_voices() -> list[dict]:
    """Return available edge-tts voices (English subset)."""
    voices = await edge_tts.list_voices()
    return [
        {
            "id": v["ShortName"],
            "name": v["FriendlyName"],
            "gender": v["Gender"],
            "locale": v["Locale"],
        }
        for v in voices
        if v["Locale"].startswith("en")
    ]


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("BACKEND_PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
