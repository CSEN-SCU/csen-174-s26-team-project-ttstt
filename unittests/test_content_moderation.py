from __future__ import annotations

from apps.bot.content_moderation import Disposition, moderate_for_tts


def test_tts_blocks_sensitive_and_urls() -> None:
    assert moderate_for_tts("I want to die").disposition is Disposition.BLOCKED
    assert moderate_for_tts("go to https://evil.test").disposition is Disposition.BLOCKED
    assert moderate_for_tts("hello team").disposition is Disposition.PUBLIC
