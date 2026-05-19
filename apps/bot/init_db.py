"""Create Postgres tables required by the bot. Run once per database."""

from __future__ import annotations

import asyncio
import os
import sys

from dotenv import load_dotenv

from apps.bot.db import ensure_voice_preferences_schema


async def _run() -> None:
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Set DATABASE_URL in .env (e.g. postgresql://app:app@localhost:5432/app)", file=sys.stderr)
        raise SystemExit(1)

    try:
        import asyncpg
    except ImportError as exc:
        print("Install asyncpg: pip install -r apps/bot/requirements.txt", file=sys.stderr)
        raise SystemExit(1) from exc

    pool = await asyncpg.create_pool(dsn=database_url, min_size=1, max_size=1)
    try:
        await ensure_voice_preferences_schema(pool)
    finally:
        await pool.close()

    print("Database ready: bot_voice_preferences table exists.")


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
