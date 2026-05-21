# TTSTT (Text To Speech To Text)

By: Noelle Evanich, Diego Silva, Dana Steinke

TTSTT is a Discord-first accessibility project that brings **text into voice**:

- **Text -> Speech:** read selected users' text messages aloud in voice channels with per-user synthetic voices.

Speech-to-text is not part of the deployable bot today; see [`docs/product-vision.md`](docs/product-vision.md).

## Current status

This repository contains a working deployable Discord bot at [`apps/bot`](apps/bot):

- Voice control commands: `/join`, `/leave`, `/status`
- TTS listener controls: `/tts_listen_user`, `/tts_stop_listening_user`, `/tts_stop_all_listeners`
- Per-user voice preferences (Postgres-backed): `/tts_voice_set`, `/tts_voice_show`, `/tts_voice_reset`

See [`apps/bot/README.md`](apps/bot/README.md) for setup and usage.

## Repository layout

| Location | Purpose |
|---|---|
| [`apps/bot`](apps/bot) | Consolidated deployable Discord bot implementation |
| [`infra`](infra) | Local Postgres Docker Compose for bot development |
| [`docs`](docs) | Product vision, architecture notes, and course artifacts |
| [`prototypes`](prototypes) | Earlier member prototypes and experiments |

## Quick start (bot)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r apps/bot/requirements.txt
python -m apps.bot.main
```

Required env vars in `.env`:

- `DISCORD_TOKEN`
- `DEEPGRAM_API_KEY`
- `DATABASE_URL`
- Optional: `FFMPEG_EXECUTABLE` (defaults to `ffmpeg`)

Before first run, create the Postgres table:

```bash
cat apps/bot/sql/voice_preferences.sql | docker compose -f infra/docker-compose.yml exec -T postgres psql -U app -d app
```
