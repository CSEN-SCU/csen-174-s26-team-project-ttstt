# API — Whisper STT, Piper TTS, auth, preferences

Backend for the Mumble voice assistant stack. Replace stubs with real Whisper and Piper integration.

## Development

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
uvicorn mumble_assistant_api.main:app --reload --port 8000
```

Health check: `GET http://127.0.0.1:8000/health`

## Environment

Copy `.env.example` to `.env` and set secrets (never commit `.env`).
