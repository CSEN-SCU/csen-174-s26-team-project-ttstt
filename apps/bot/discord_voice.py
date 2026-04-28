"""Discord voice connection helpers for bot workflows."""

from __future__ import annotations

from typing import Protocol


class DiscordVoiceClient(Protocol):
    """Minimal client contract for connecting and reading a voice stream."""

    def authenticate(self, token: str) -> None:
        """Authenticate with Discord using the provided bot token."""

    def join_only_voice_channel(self) -> None:
        """Join the single configured voice channel used for testing."""

    def get_audio_stream(self) -> object:
        """Return a stream-like object for incoming voice audio."""


def connect_join_and_get_audio_stream(token: str, voice_client: DiscordVoiceClient) -> object:
    """
    Authenticate, join the single voice channel, and return an audio stream.

    This is a future-friendly seam for real Discord SDK integration while
    keeping orchestration easy to unit test.
    """
    voice_client.authenticate(token)
    voice_client.join_only_voice_channel()
    return voice_client.get_audio_stream()
