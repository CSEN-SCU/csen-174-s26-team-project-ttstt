from __future__ import annotations

import pytest

import apps.bot.main as bot_main


class _FakePool:
    def __init__(self) -> None:
        self.closed = False

    async def close(self) -> None:
        self.closed = True


def test_main_closes_pool_if_bot_construction_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_pool = _FakePool()

    async def fake_create_postgres_pool(database_url: str) -> object:
        assert database_url == "postgresql://example"
        return fake_pool

    class BoomRelayBot:
        def __init__(self, **kwargs: object) -> None:
            raise RuntimeError("constructor boom")

    monkeypatch.setenv("DISCORD_TOKEN", "token")
    monkeypatch.setenv("DEEPGRAM_API_KEY", "deepgram-key")
    monkeypatch.setenv("DATABASE_URL", "postgresql://example")
    monkeypatch.setenv("HELP_URL", "https://example.netlify.app")
    monkeypatch.setattr(bot_main, "create_postgres_pool", fake_create_postgres_pool)
    monkeypatch.setattr(bot_main, "RelayBot", BoomRelayBot)

    with pytest.raises(RuntimeError, match="constructor boom"):
        import asyncio

        asyncio.run(bot_main.main())

    assert fake_pool.closed
