"""Azure Speech neural TTS — synthesize text to WAV bytes for Discord playback."""

from __future__ import annotations

import os

import azure.cognitiveservices.speech as speechsdk


class TTSError(Exception):
    """Raised when Azure Speech synthesis fails."""


def synthesize_to_wav_bytes(text: str) -> bytes:
    """Return RIFF WAV audio bytes for ``text`` using Azure neural TTS."""
    stripped = text.strip()
    if not stripped:
        raise TTSError("Text is empty.")

    key = os.getenv("AZURE_SPEECH_KEY")
    region = os.getenv("AZURE_SPEECH_REGION")
    voice = os.getenv("AZURE_TTS_VOICE", "en-US-JennyNeural")

    if not key or not region:
        raise TTSError("Set AZURE_SPEECH_KEY and AZURE_SPEECH_REGION in prototypes/diego/.env")

    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    speech_config.speech_synthesis_voice_name = voice
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm
    )

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=None,
    )
    result = synthesizer.speak_text_async(stripped).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        data = result.audio_data
        if not data:
            raise TTSError("Azure returned no audio data.")
        return data

    if result.reason == speechsdk.ResultReason.Canceled:
        details = result.cancellation_details
        msg = details.error_details or str(details.reason)
        raise TTSError(msg)

    raise TTSError(f"Unexpected synthesis result: {result.reason}")
