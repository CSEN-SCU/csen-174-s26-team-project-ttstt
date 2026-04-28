"""
Future-facing unit test for Discord voice connection behavior.

This test defines the expected flow for:
- authenticating with a Discord key/token,
- joining the single available test voice channel,
- and receiving an audio stream from that channel.
"""

from __future__ import annotations

import importlib
from typing import Callable

import pytest


MODULE_PATH = "apps.bot.discord_voice"
FUNCTION_NAME = "connect_join_and_get_audio_stream"


def _load_connect_flow() -> Callable:
    """
    Load the future Discord voice connection function once it exists.
    """
    try:
        module = importlib.import_module(MODULE_PATH)
    except ModuleNotFoundError:
        pytest.skip(
            f"{MODULE_PATH!r} does not exist yet. "
            "Unskip this test after Discord voice integration is implemented."
        )

    if not hasattr(module, FUNCTION_NAME):
        pytest.skip(
            f"{MODULE_PATH!r} exists, but {FUNCTION_NAME!r} is not implemented yet."
        )

    return getattr(module, FUNCTION_NAME)


def test_connect_join_and_get_audio_stream_single_server_single_voice_channel() -> None:
    # As a Discord user, I can connect the bot with my key, join the voice chat, and receive an audio stream for transcription.

    # Arrange
    connect_flow = _load_connect_flow()

    class FakeDiscordVoiceClient:
        def __init__(self) -> None:
            self.authenticated_with: str | None = None
            self.joined_voice = False
            self.audio_stream = object()

        def authenticate(self, token: str) -> None:
            self.authenticated_with = token

        def join_only_voice_channel(self) -> None:
            self.joined_voice = True

        def get_audio_stream(self) -> object:
            return self.audio_stream

    fake_client = FakeDiscordVoiceClient()
    fake_token = "test_discord_token"

    # Action
    stream = connect_flow(fake_token, fake_client)

    # Assert
    assert fake_client.authenticated_with == fake_token
    assert fake_client.joined_voice is True
    assert stream is fake_client.audio_stream


def test_connect_join_and_get_audio_stream_calls_steps_in_required_order() -> None:
    # As a Discord user, the bot authenticates before joining and only then starts reading voice audio.

    # Arrange
    connect_flow = _load_connect_flow()
    call_log: list[str] = []

    class FakeDiscordVoiceClient:
        def authenticate(self, token: str) -> None:
            call_log.append(f"authenticate:{token}")

        def join_only_voice_channel(self) -> None:
            call_log.append("join_only_voice_channel")

        def get_audio_stream(self) -> object:
            call_log.append("get_audio_stream")
            return object()

    fake_client = FakeDiscordVoiceClient()

    # Action
    connect_flow("ordered_token", fake_client)

    # Assert
    assert call_log == [
        "authenticate:ordered_token",
        "join_only_voice_channel",
        "get_audio_stream",
    ]
