# TTSTT Bot (Deployable Skeleton)

This is a deployable Discord bot baseline based on `prototypes/noelle`, now with
commanded text-to-speech listener support.

## Current Commands

- `/help` - Link to the public help guide (GitHub Pages).
- `/join` - Join the command invoker's current voice channel.
- `/leave` - Disconnect from voice in the current server.
- `/status` - Report current voice connection status for the server.
- `/tts_listen_user <user>` - Start reading text messages from a selected user in the control channel.
- `/tts_stop_listening_user <user>` - Stop reading one selected user's messages.
- `/tts_stop_all_listeners` - Stop reading all configured users in the server.
- `/tts_voice_set` - Set your own TTS voice/model, speed, pitch, and style for the current server.
- `/tts_voice_show` - Show your saved TTS settings for the current server.
- `/tts_voice_reset` - Reset your TTS settings to defaults for the current server.
- `/stt_listen_user <user>` - Start transcribing a user's voice to the control text channel.
- `/stt_stop_listening_user <user>` - Stop transcribing one user.
- `/stt_stop_all_listeners` - Stop transcribing all users in the server.

Public help site: https://csen-scu.github.io/csen-174-s26-team-project-ttstt/ (see [`docs/help`](../../docs/help)).

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
   - Optional: `OPENAI_API_KEY` (enables OpenAI Moderation API checks on STT/TTS text)
   - Optional: `HELP_URL` (defaults to the GitHub Pages help site for `/help`)

## Privacy and content safety

- `/join` warns that STT and TTS features transcribe or read aloud user content in the server.
- **STT:** Transcripts matching self-harm, medical, or minor-disclosure patterns are not posted publicly; the speaker gets a private DM (with a 988 crisis line for self-harm matches). `http://` and `https://` URLs are replaced with `[link removed]` in public posts.
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

   **Debug captured voice:** set `STT_DEBUG_SAVE_WAV=1` in `.env`. Each STT utterance is written to `stt_debug_audio/` as a WAV file (48 kHz stereo). Play with `ffplay stt_debug_audio/<file>.wav` or any audio player.

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
Optional: `HELP_URL` for the `/help` command link.
