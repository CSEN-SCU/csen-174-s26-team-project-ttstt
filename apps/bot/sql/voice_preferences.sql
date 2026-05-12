CREATE TABLE IF NOT EXISTS bot_voice_preferences (
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    voice TEXT NOT NULL,
    speed DOUBLE PRECISION NOT NULL,
    pitch DOUBLE PRECISION NOT NULL,
    style TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (guild_id, user_id)
);
