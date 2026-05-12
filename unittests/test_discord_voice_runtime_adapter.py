from __future__ import annotations

import importlib
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _load_runtime_client():
    module = importlib.import_module("apps.bot.discord_voice")
    return module.DiscordRuntimeVoiceClient


def test_runtime_voice_client_connects_and_returns_stream() -> None:
    runtime_client = _load_runtime_client()
    call_log: list[str] = []
    expected_stream = object()

    def connect() -> None:
        call_log.append("connect")

    def stream_reader() -> object:
        call_log.append("stream")
        return expected_stream

    client = runtime_client(connect, stream_reader)

    client.authenticate("token")
    client.join_only_voice_channel()
    stream = client.get_audio_stream()

    assert call_log == ["connect", "stream"]
    assert stream is expected_stream


def test_runtime_voice_client_requires_authenticate_before_join() -> None:
    runtime_client = _load_runtime_client()
    client = runtime_client(lambda: None, lambda: object())

    try:
        client.join_only_voice_channel()
    except RuntimeError as exc:
        assert "authenticate" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError when joining before authenticate")
