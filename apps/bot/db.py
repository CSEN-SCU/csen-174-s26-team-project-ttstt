"""Database helpers for bot runtime."""

from __future__ import annotations

import logging
from pathlib import Path

LOGGER = logging.getLogger("ttstt-bot.db")

_SCHEMA_SQL = Path(__file__).resolve().parent / "sql" / "voice_preferences.sql"


async def create_postgres_pool(database_url: str) -> object:
    """Create an asyncpg connection pool and ensure required tables exist."""
    if not database_url:
        raise ValueError("DATABASE_URL is required")
    try:
        import asyncpg
    except Exception as exc:  # pragma: no cover - import depends on environment
        raise RuntimeError("asyncpg is required for Postgres-backed preferences") from exc
    pool = await asyncpg.create_pool(dsn=database_url, min_size=1, max_size=5)
    await ensure_voice_preferences_schema(pool)
    return pool


async def ensure_voice_preferences_schema(pool: object) -> None:
    """Create bot_voice_preferences if this database has not been initialized."""
    if not _SCHEMA_SQL.is_file():
        raise RuntimeError(f"Missing schema file: {_SCHEMA_SQL}")

    ddl = _SCHEMA_SQL.read_text(encoding="utf-8")
    async with pool.acquire() as conn:  # type: ignore[union-attr]
        await conn.execute(ddl)
    LOGGER.info("Ensured Postgres schema: bot_voice_preferences")
