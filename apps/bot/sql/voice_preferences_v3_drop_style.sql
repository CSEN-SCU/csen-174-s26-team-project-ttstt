-- Remove unused style column. Safe to re-run.
ALTER TABLE bot_voice_preferences
    DROP COLUMN IF EXISTS style;
