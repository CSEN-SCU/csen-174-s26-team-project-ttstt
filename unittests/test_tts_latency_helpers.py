from __future__ import annotations

from apps.bot.tts import preprocess_text_for_tts, split_text_for_progressive_tts


def test_preprocess_text_for_tts_removes_urls_and_normalizes_spaces() -> None:
    raw = "Check   this https://example.com/test   now"

    processed = preprocess_text_for_tts(raw)

    assert "https://example.com/test" not in processed
    assert processed == "Check this now"


def test_split_text_for_progressive_tts_prioritizes_smaller_first_chunk() -> None:
    text = "one two three four five six seven eight nine ten eleven twelve"

    chunks = split_text_for_progressive_tts(text, first_chunk_chars=18, max_chars=30)

    assert chunks
    assert len(chunks[0]) <= 18
    assert all(len(chunk) <= 30 for chunk in chunks[1:])
    assert " ".join(chunks).replace("  ", " ").strip() == text
