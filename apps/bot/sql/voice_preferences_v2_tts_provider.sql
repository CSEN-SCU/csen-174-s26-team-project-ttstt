-- Add per-user TTS engine selection (deepgram | piper). Safe to re-run.
ALTER TABLE bot_voice_preferences
    ADD COLUMN IF NOT EXISTS tts_provider TEXT NOT NULL DEFAULT 'deepgram';
