"""Content safety checks for TTS playback."""

from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from enum import Enum

LOGGER = logging.getLogger(__name__)

URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)

_SELF_HARM_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b(kill\s+myself|suicide|self[- ]?harm|want\s+to\s+die)\b", re.I),
    re.compile(r"\bhurt(ing)?\s+(myself|me)\b", re.I),
    re.compile(r"\b(thinking\s+about|been)\s+.+\s+(hurt|kill)\s+(myself|me)\b", re.I),
)

_SENSITIVE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"\b(bipolar|schizophrenia|ptsd|adhd|autism|diagnosed\s+with|mental\s+illness)\b",
        re.I,
    ),
    re.compile(r"\b(stopped|stop(ped)?)\s+(taking|my)\s+(medication|meds|medicine)\b", re.I),
    re.compile(r"\b(i\s+have\s+.+\s+disorder)\b", re.I),
    re.compile(r"\bi(?:'m| am)\s+(?:only\s+)?(\d{1,2})\b", re.I),
    re.compile(r"\bi(?:'m| am)\s+a\s+minor\b", re.I),
    re.compile(r"\bmy\s+parents\s+don'?t\s+know\b", re.I),
)

_OPENAI_BLOCK_CATEGORIES = frozenset(
    {"hate", "harassment", "violence", "sexual", "sexual/minors", "illicit", "illicit/violent"}
)
_OPENAI_SENSITIVE_CATEGORIES = frozenset({"self-harm", "self-harm/intent", "self-harm/instructions"})
_OPENAI_SCORE_THRESHOLD = 0.75


class Disposition(str, Enum):
    PUBLIC = "public"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class ModerationOutcome:
    disposition: Disposition
    public_text: str | None = None
    user_message: str | None = None
    log_reason: str = ""


def contains_url(text: str) -> bool:
    return bool(URL_PATTERN.search(text))


def matches_self_harm(text: str) -> bool:
    return any(pattern.search(text) for pattern in _SELF_HARM_PATTERNS)


def matches_sensitive(text: str) -> bool:
    if matches_self_harm(text):
        return True
    return any(pattern.search(text) for pattern in _SENSITIVE_PATTERNS)


def _openai_moderation_flags(text: str, api_key: str) -> tuple[bool, bool]:
    """Return (should_block, is_self_harm) from OpenAI Moderation API."""

    payload = json.dumps({"input": text}).encode()
    request = urllib.request.Request(
        "https://api.openai.com/v1/moderations",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            body = json.loads(response.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        LOGGER.warning("OpenAI moderation request failed: %s", exc)
        return False, False

    results = body.get("results") or []
    if not results:
        return False, False

    scores: dict[str, float] = results[0].get("category_scores") or {}
    flagged: dict[str, bool] = results[0].get("categories") or {}

    self_harm = any(
        scores.get(category, 0.0) >= _OPENAI_SCORE_THRESHOLD or flagged.get(category, False)
        for category in _OPENAI_SENSITIVE_CATEGORIES
    )
    should_block = any(
        scores.get(category, 0.0) >= _OPENAI_SCORE_THRESHOLD or flagged.get(category, False)
        for category in _OPENAI_BLOCK_CATEGORIES
    )
    return should_block, self_harm


def _apply_openai_tts(text: str, api_key: str | None) -> ModerationOutcome | None:
    if not api_key:
        return None

    should_block, self_harm = _openai_moderation_flags(text, api_key)
    if self_harm:
        return ModerationOutcome(
            disposition=Disposition.BLOCKED,
            user_message="This message cannot be read aloud because it may involve self-harm.",
            log_reason="openai_self_harm",
        )
    if should_block:
        return ModerationOutcome(
            disposition=Disposition.BLOCKED,
            user_message="This message was blocked by content safety checks.",
            log_reason="openai_policy",
        )
    return None


def moderate_for_tts(text: str, *, openai_api_key: str | None = None) -> ModerationOutcome:
    """Decide whether text may be synthesized and played in a voice channel."""

    stripped = text.strip()
    if not stripped:
        return ModerationOutcome(
            disposition=Disposition.BLOCKED,
            user_message="Message is empty.",
            log_reason="empty",
        )

    openai_result = _apply_openai_tts(stripped, openai_api_key)
    if openai_result is not None:
        return openai_result

    if matches_sensitive(stripped):
        return ModerationOutcome(
            disposition=Disposition.BLOCKED,
            user_message="This message cannot be read aloud because it may contain sensitive content.",
            log_reason="sensitive_keywords",
        )

    if contains_url(stripped):
        return ModerationOutcome(
            disposition=Disposition.BLOCKED,
            user_message="Messages containing links cannot be read aloud.",
            log_reason="url_present",
        )

    return ModerationOutcome(
        disposition=Disposition.PUBLIC,
        public_text=stripped,
        log_reason="allowed",
    )
