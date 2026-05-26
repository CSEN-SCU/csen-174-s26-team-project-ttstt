from __future__ import annotations

import asyncio

import pytest

import apps.bot.main as bot_main
from apps.bot.main import tts_stop_listening
from apps.bot.tts_listener_registry import TtsListenerRegistry


class _FakeResponse:
    def __init__(self) -> None:
        self.messages: list[tuple[str, bool]] = []

    async def send_message(self, content: str, *, ephemeral: bool = False, **_kwargs: object) -> None:
        self.messages.append((content, ephemeral))


class _FakeUser:
    def __init__(self, user_id: int) -> None:
        self.id = user_id


class _FakeGuild:
    def __init__(self, guild_id: int) -> None:
        self.id = guild_id


class _FakeInteraction:
    def __init__(self, *, client: object, guild_id: int, invoker_id: int) -> None:
        self.client = client
        self.guild = _FakeGuild(guild_id)
        self.user = _FakeUser(invoker_id)
        self.response = _FakeResponse()


class _FakeBot:
    def __init__(self) -> None:
        self.listeners = TtsListenerRegistry()


def test_stop_listening_only_affects_invoker(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(bot_main, "RelayBot", _FakeBot)
    bot = _FakeBot()
    interaction = _FakeInteraction(client=bot, guild_id=123, invoker_id=111)

    bot.listeners.add(guild_id=123, user_id=111)
    bot.listeners.add(guild_id=123, user_id=222)

    async def run() -> None:
        await tts_stop_listening.callback(interaction)  # type: ignore[arg-type]
        assert interaction.response.messages[-1] == ("Stopped listening to your messages.", True)
        assert not bot.listeners.contains(guild_id=123, user_id=111)
        assert bot.listeners.contains(guild_id=123, user_id=222)

        await tts_stop_listening.callback(interaction)  # type: ignore[arg-type]
        assert interaction.response.messages[-1] == ("You are not currently being listened to.", True)

    asyncio.run(run())
