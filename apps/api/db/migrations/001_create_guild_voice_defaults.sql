CREATE TABLE IF NOT EXISTS guild_voice_defaults (
    guild_id BIGINT PRIMARY KEY,
    voice_id TEXT NOT NULL,
    stability DOUBLE PRECISION NOT NULL CHECK (stability >= 0.0 AND stability <= 1.0),
    speed DOUBLE PRECISION NOT NULL CHECK (speed >= 0.7 AND speed <= 1.2),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
