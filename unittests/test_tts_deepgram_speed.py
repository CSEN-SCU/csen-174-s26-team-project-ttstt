"""Unit tests for Deepgram speed clamping."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from apps.bot.tts import (
    DEEPGRAM_MAX_SPEED,
    DEEPGRAM_MIN_SPEED,
    DeepgramTtsClient,
    clamp_deepgram_speed,
)


def test_clamp_deepgram_speed_bounds() -> None:
    assert clamp_deepgram_speed(0.5) == DEEPGRAM_MIN_SPEED
    assert clamp_deepgram_speed(0.69) == DEEPGRAM_MIN_SPEED
    assert clamp_deepgram_speed(2.0) == DEEPGRAM_MAX_SPEED
    assert clamp_deepgram_speed(1.8) == DEEPGRAM_MAX_SPEED
    assert clamp_deepgram_speed(1.0) == 1.0


@patch("apps.bot.tts.inspect.signature")
@patch.object(DeepgramTtsClient, "_get_client")
def test_deepgram_synthesize_clamps_speed_before_api_call(
    get_client: MagicMock,
    signature: MagicMock,
) -> None:
    signature.return_value.parameters = {
        "model": object(),
        "text": object(),
        "encoding": object(),
        "container": object(),
        "speed": object(),
    }
    generate_fn = MagicMock(return_value=[b"wav-bytes"])
    get_client.return_value.speak.v1.audio.generate = generate_fn

    client = DeepgramTtsClient(api_key="test-key")
    client.synthesize("hello", {"voice": "aura-2-thalia-en", "speed": 0.5})

    assert generate_fn.call_args.kwargs["speed"] == DEEPGRAM_MIN_SPEED


@patch("apps.bot.tts.inspect.signature")
@patch.object(DeepgramTtsClient, "_get_client")
def test_deepgram_synthesize_omits_speed_when_unset(
    get_client: MagicMock,
    signature: MagicMock,
) -> None:
    signature.return_value.parameters = {
        "model": object(),
        "text": object(),
        "encoding": object(),
        "container": object(),
        "speed": object(),
    }
    generate_fn = MagicMock(return_value=[b"wav-bytes"])
    get_client.return_value.speak.v1.audio.generate = generate_fn

    client = DeepgramTtsClient(api_key="test-key")
    client.synthesize("hello", {"voice": "aura-2-thalia-en"})

    assert "speed" not in generate_fn.call_args.kwargs
