from __future__ import annotations

from apps.bot.content_moderation import (
    Disposition,
    moderate_for_transcript,
    moderate_for_tts,
    redact_urls,
)


def test_redact_urls() -> None:
    text = "check out http://malicious-example.com please"
    assert redact_urls(text) == "check out [link removed] please"


def test_transcript_sensitive_self_harm_goes_to_dm() -> None:
    outcome = moderate_for_transcript("I've been thinking about hurting myself lately")
    assert outcome.disposition is Disposition.PRIVATE_DM
    assert outcome.crisis_footer is not None


def test_transcript_sensitive_medical_goes_to_dm() -> None:
    outcome = moderate_for_transcript("I have bipolar disorder and stopped my medication")
    assert outcome.disposition is Disposition.PRIVATE_DM
    assert outcome.crisis_footer is None


def test_transcript_url_redacted_for_public() -> None:
    outcome = moderate_for_transcript("visit https://example.com now")
    assert outcome.disposition is Disposition.PUBLIC
    assert outcome.public_text == "visit [link removed] now"


def test_tts_blocks_sensitive_and_urls() -> None:
    assert moderate_for_tts("I want to die").disposition is Disposition.BLOCKED
    assert moderate_for_tts("go to https://evil.test").disposition is Disposition.BLOCKED
    assert moderate_for_tts("hello team").disposition is Disposition.PUBLIC
