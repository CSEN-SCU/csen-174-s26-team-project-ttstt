# TTSTT Bot (Deployable Skeleton)

This is a deployable Discord bot baseline based on `prototypes/noelle`, now with
commanded text-to-speech listener support.

## Current Commands

- `/help` - Link to the public help guide (Netlify).
- `/join` - Join the command invoker's current voice channel.
- `/leave` - Disconnect from voice in the current server.
- `/status` - Report current voice connection status for the server.
- `/tts_listen_user <user>` - Start reading text messages from a selected user in the control channel.
- `/tts_stop_listening` - Stop reading your own messages.
- `/tts_voice_set` - Set your own TTS voice/model, speed, pitch, and style for the current server (partial updates; use style `none` to clear).
- `/tts_voice_show` - Show your saved TTS settings for the current server.
- `/tts_voice_reset` - Reset your TTS settings to defaults for the current server.

Public help site: hosted on Netlify (see [`docs/help`](../../docs/help)); set `HELP_URL` in `.env` to your Netlify URL.

## Requirements

- Python 3.11+
- FFmpeg + Opus runtime available for Discord voice
- Discord bot token with Guilds, Voice States, and Message Content intents enabled
- Deepgram API key
- PostgreSQL database

## Local Setup

1. Create a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r apps/bot/requirements.txt
   ```

3. Configure environment:

   ```bash
   touch .env
   ```

   Then set the following in `.env`:

   - `DISCORD_TOKEN`
   - `DEEPGRAM_API_KEY`
   - `DATABASE_URL`
   - Optional: `FFMPEG_EXECUTABLE` (defaults to `ffmpeg`)
   - Optional: `OPENAI_API_KEY` (enables OpenAI Moderation API checks on TTS text)
   - `HELP_URL` (your Netlify help site URL; required for `/help`)

## Privacy and content safety

- `/join` warns that TTS may read aloud user messages in the server.
- **TTS:** Listened messages with sensitive content or links are not synthesized or played in voice.
- Set `OPENAI_API_KEY` for additional hate/harassment/violence screening via OpenAI's Moderation API.

4. Start Postgres (if using local Docker):

   ```bash
   docker compose -f infra/docker-compose.yml up -d
   ```

   Example `DATABASE_URL`: `postgresql://app:app@localhost:5432/app`

5. Initialize the database (once per `DATABASE_URL`; also runs automatically on bot startup):

   ```bash
   python -m apps.bot.init_db
   ```

6. Run the bot:

   ```bash
   python -m apps.bot.main
   ```

   On startup you should see `Ensured Postgres schema: bot_voice_preferences` in the logs.

## Testing

Run the unit suite:

```bash
python -m pytest -q unittests
```

Optional live Deepgram integration test:

```bash
RUN_LIVE_DEEPGRAM_TEST=1 python -m pytest -q unittests/test_tts_deepgram_live.py
```

This test makes a real network request and validates a WAV response.

## Container Deployment

Use this simple image for deployment targets that support Docker:

```dockerfile
FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r apps/bot/requirements.txt

CMD ["python", "-m", "apps.bot.main"]
```

Set `DISCORD_TOKEN` in your runtime environment/secrets manager.
Also set `DEEPGRAM_API_KEY` and `DATABASE_URL`.
Required: `HELP_URL` — your Netlify help site URL for `/help`.
