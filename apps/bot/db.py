"""Database helpers for bot runtime."""

from __future__ import annotations

async def create_postgres_pool(database_url: str) -> object:
    """Create an asyncpg connection pool lazily."""
    if not database_url:
        raise ValueError("DATABASE_URL is required")
    try:
        import asyncpg
    except Exception as exc:  # pragma: no cover - import depends on environment
        raise RuntimeError("asyncpg is required for Postgres-backed preferences") from exc
    return await asyncpg.create_pool(dsn=database_url, min_size=1, max_size=5)
