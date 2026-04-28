"""
Unit test for handling TTS provider errors. (Starts RED until TTS implementation is added)
"""

import importlib

import pytest

MODULE_PATH = "apps.bot.tts"
FUNCTION_NAME = "synthesize_text"


def _load_synthesize_text():
    try:
        module = importlib.import_module(MODULE_PATH)
    except ModuleNotFoundError:
        pytest.fail(
            f"{MODULE_PATH!r} not implemented yet. "
            "Implement TTS module to turn this RED contract into a real behavior test."
        )

    if not hasattr(module, FUNCTION_NAME):
        pytest.fail(
            f"{FUNCTION_NAME!r} not implemented yet in {MODULE_PATH!r}. "
            "Add function implementation to satisfy this test."
        )

    return getattr(module, FUNCTION_NAME)


def test_synthesize_text_maps_provider_failure_to_user_safe_error() -> None:
    # As a voice-channel listener, if the TTS fails, I get a clear failure path instead of the bot crashing.

    # Arrange
    synthesize_text = _load_synthesize_text()

    class FakeProviderTimeout(Exception):
        pass

    class FakeTtsClient:
        def __init__(self) -> None:
            self.called_with: bytes | None = None

        def synthesize(self, text: str, voice_prefs: dict) -> bytes:
            raise FakeProviderTimeout("TTS provider timed out")

    text = "Please read this message aloud."
    voice_prefs = {
        "voice": "calm",
        "speed": 1.0,
        "pitch": 0.0,
    }
    client = FakeTtsClient()

    # Action
    with pytest.raises(Exception) as e:
        synthesize_text(text, voice_prefs, client)

    # Assert
    assert isinstance(e.value, Exception)
    assert str(e.value) == "TTS provider timed out"
    