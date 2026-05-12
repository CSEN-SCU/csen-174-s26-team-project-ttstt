"""ElevenLabs implementation of the bot's TTS client contract."""

from __future__ import annotations

import httpx


class ElevenLabsTtsError(Exception):
    """Raised when an ElevenLabs synthesis request cannot be fulfilled."""


class ElevenLabsTtsClient:
    """Synchronous ElevenLabs TTS client.

    The class is synchronous on purpose: the bot calls ``synthesize`` from
    ``asyncio.to_thread`` so the Discord gateway keeps responding while audio
    is being generated. Returned bytes are MP3-encoded (``audio/mpeg``).
    """

    BASE_URL = "https://api.elevenlabs.io/v1/text-to-speech"

    def __init__(
        self,
        api_key: str,
        default_voice_id: str,
        default_model_id: str = "eleven_turbo_v2_5",
        timeout_s: float = 30.0,
    ) -> None:
        if not api_key:
            raise ValueError("ElevenLabs api_key is required.")
        if not default_voice_id:
            raise ValueError("ElevenLabs default_voice_id is required.")

        self._api_key = api_key
        self._default_voice_id = default_voice_id
        self._default_model_id = default_model_id
        self._timeout_s = timeout_s

    def synthesize(self, text: str, voice_prefs: dict) -> bytes:
        stripped = text.strip()
        if not stripped:
            raise ElevenLabsTtsError("Text is empty.")

        voice_id = voice_prefs.get("voice_id") or self._default_voice_id
        model_id = voice_prefs.get("model_id") or self._default_model_id

        voice_settings: dict = {}
        for key in ("stability", "similarity_boost", "style"):
            if key in voice_prefs and voice_prefs[key] is not None:
                voice_settings[key] = voice_prefs[key]
        if "use_speaker_boost" in voice_prefs and voice_prefs["use_speaker_boost"] is not None:
            voice_settings["use_speaker_boost"] = bool(voice_prefs["use_speaker_boost"])

        body: dict = {"text": stripped, "model_id": model_id}
        if voice_settings:
            body["voice_settings"] = voice_settings

        url = f"{self.BASE_URL}/{voice_id}"
        headers = {
            "xi-api-key": self._api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }

        try:
            response = httpx.post(url, headers=headers, json=body, timeout=self._timeout_s)
        except httpx.HTTPError as exc:
            raise ElevenLabsTtsError(f"ElevenLabs request failed: {exc}") from exc

        if response.status_code >= 400:
            detail = response.text[:300] if response.text else "<no body>"
            raise ElevenLabsTtsError(
                f"ElevenLabs returned HTTP {response.status_code}: {detail}"
            )

        audio = response.content
        if not audio:
            raise ElevenLabsTtsError("ElevenLabs returned an empty audio body.")
        return audio
