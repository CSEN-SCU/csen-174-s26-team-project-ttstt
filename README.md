# TTSTT (Text To Speech To Text)

Mumble voice chat plus a **FastAPI** backend: **Whisper** for speech-to-text, **Piper** (Hugging Face voices) for text-to-speech, per-user voice settings, and planned **ffmpeg** step (pitch/tempo + loudness normalization). The browser client is based on **mumble-web**; voice relay uses **Murmur**.

**Status:** API and web integration are still being built. `GET /health` on the API is available today.

## Features (roadmap)

- Post spoken audio to an API → transcribe with Whisper → send text in Mumble chat  
- Read chat aloud with Piper; optional server-side pitch/tempo and default loudnorm  
- Store voice / prosody preferences per user (Postgres)

## Stack

Python (FastAPI), Node (mumble-web), Docker Compose (Murmur + Postgres), OpenAI Whisper (or compatible API), Piper ONNX from Hugging Face.

## Quick start

1. **Infrastructure** — from [`infra`](infra): `docker compose up -d` (see [`infra/README.md`](infra/README.md)).  
2. **API** — from [`apps/api`](apps/api): venv, `pip install -e ".[dev]"`, run `uvicorn` (see [`apps/api/README.md`](apps/api/README.md)).  
3. **Web client** — from [`apps/web`](apps/web): install deps and run/build per [`apps/web/README.md`](apps/web/README.md).

Mumble default port: **64738**. API health check: `http://127.0.0.1:8000/health`

## Layout

| Directory | Role |
|-----------|------|
| `apps/api` | Backend (Whisper, Piper, DB) |
| `apps/web` | Mumble web client |
| `infra` | Docker Compose (Murmur, Postgres) |
| `docs` | Project notes and journal |

Optional upstream Mumble **desktop** source is not in this repo; see [`vendor/README.md`](vendor/README.md).
