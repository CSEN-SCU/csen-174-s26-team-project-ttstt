from __future__ import annotations

import asyncio

from apps.bot.main import GuildMessageSerializer


def test_guild_message_serializer_serializes_same_guild() -> None:
    serializer = GuildMessageSerializer()
    events: list[str] = []

    async def first() -> None:
        events.append("first:start")
        await asyncio.sleep(0)
        events.append("first:end")

    async def second() -> None:
        events.append("second:start")
        await asyncio.sleep(0)
        events.append("second:end")

    async def runner() -> None:
        await asyncio.gather(
            serializer.run(1, first()),
            serializer.run(1, second()),
        )

    asyncio.run(runner())
    assert events == ["first:start", "first:end", "second:start", "second:end"] or events == [
        "second:start",
        "second:end",
        "first:start",
        "first:end",
    ]
