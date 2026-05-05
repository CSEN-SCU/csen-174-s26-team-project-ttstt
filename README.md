[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/NfqHRKdw)
# TTSTT (Text To Speech To Text)

By: Noelle Evanich, Diego Silva, Dana Steinke

**CSEN 174 — planning / design phase.** This repository documents the **intended** product; **there is no application code here yet** (the `apps/` tree has been removed until implementation begins).

## Intended product (summary)

A **Discord bot** plus a **backend service** so participants can:

- Turn **voice** into **text** in a server (via **automatic speech recognition**, e.g. Whisper-class APIs).
- Hear **text chat** read aloud in **voice channels** (**neural text-to-speech**, e.g. Piper-style models from Hugging Face), with per-user voice and prosody settings.
- Apply optional **server-side audio post-processing** (e.g. ffmpeg: pitch/tempo, default loudness normalization).

The course-facing **product vision** and rationale are in **[`docs/product-vision.md`](docs/product-vision.md)**.

## What is in this repo right now

| Location | Contents |
|----------|----------|
| [`docs/`](docs) | Product vision, learning journal, and other course artifacts |
| [`infra/`](infra) | Example **Docker Compose** for **Postgres** (for when the backend is implemented) — optional local dev database |

## Implementation status (current)

The repository now includes an initial product scaffolding under `apps/` for:
- ASR transcription seam (`apps/bot/transcription.py`)
- Discord voice seam (`apps/bot/discord_voice.py`)
- ElevenLabs TTS integration and setting validation (`apps/bot/tts.py`)
- Preference resolution + guild-default persistence abstractions (`apps/bot/preferences_store.py`)

## Secret safety for public demos

- Keep runtime keys in server environment variables only.
- Use `.env.example` as a template and never commit real `.env` values.
- Run `python scripts/check_no_secrets.py` before pushing to detect likely leaked keys in tracked files.

## For course staff

- **Scope:** Software engineering process (vision, architecture, testing, and deployment **to be documented** as the quarter progresses).  
- **AI:** The design centers on **speech recognition** and **speech synthesis** as the core capabilities (vendor-agnostic in documentation).  
- **Status:** **Pre-implementation** — use `docs/` and team process artifacts to assess planning; do not expect a runnable demo from this repository state alone.
