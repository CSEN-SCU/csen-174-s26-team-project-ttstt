# TTSTT Bot (Deployable Skeleton)

This is a deployable Discord bot baseline based on `prototypes/noelle`, scoped to
voice connect/disconnect control only.

It does **not** run speech-to-text, text-to-speech, or webhook relay yet.

## Current Commands

- `/join` - Join the command invoker's current voice channel.
- `/leave` - Disconnect from voice in the current server.
- `/status` - Report current voice connection status for the server.

## Requirements

- Python 3.11+
- FFmpeg + Opus runtime available for Discord voice
- Discord bot token with Guilds and Voice States intents enabled

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
   cp apps/bot/.env.example .env
   ```

   Then set `DISCORD_TOKEN` in `.env`.

4. Run the bot:

   ```bash
   python -m apps.bot.main
   ```

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
