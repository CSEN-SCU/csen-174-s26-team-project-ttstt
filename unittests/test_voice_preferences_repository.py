from __future__ import annotations

import asyncio

from apps.bot.voice_preferences import PostgresVoicePreferencesRepository, VoicePreferences


class FakeConn:
    def __init__(self) -> None:
        self.rows: dict[tuple[int, int], dict[str, object]] = {}

    async def fetchrow(self, _query: str, guild_id: int, user_id: int) -> dict[str, object] | None:
        return self.rows.get((guild_id, user_id))

    async def execute(
        self,
        _query: str,
        guild_id: int,
        user_id: int,
        voice: str,
        speed: float,
        pitch: float,
        style: str | None,
    ) -> None:
        self.rows[(guild_id, user_id)] = {
            "voice": voice,
            "speed": speed,
            "pitch": pitch,
            "style": style,
        }


def test_repository_returns_defaults_when_missing() -> None:
    repo = PostgresVoicePreferencesRepository(conn=FakeConn())

    prefs = asyncio.run(repo.get(guild_id=1, user_id=99))

    assert prefs == VoicePreferences.defaults()


def test_repository_upsert_and_reset() -> None:
    repo = PostgresVoicePreferencesRepository(conn=FakeConn())
    updated = VoicePreferences(voice="aura-2-thalia-en", speed=1.2, pitch=-2.0, style="calm")

    saved = asyncio.run(repo.upsert(guild_id=1, user_id=99, prefs=updated))
    reset = asyncio.run(repo.reset(guild_id=1, user_id=99))

    assert saved == updated
    assert reset == VoicePreferences.defaults()


def test_voice_preferences_validate_rejects_out_of_range_values() -> None:
    bad_speed = VoicePreferences(voice="aura-2-thalia-en", speed=2.5, pitch=0.0, style=None)
    bad_pitch = VoicePreferences(voice="aura-2-thalia-en", speed=1.0, pitch=99.0, style=None)

    try:
        bad_speed.validate()
        speed_failed = False
    except ValueError:
        speed_failed = True

    try:
        bad_pitch.validate()
        pitch_failed = False
    except ValueError:
        pitch_failed = True

    assert speed_failed
    assert pitch_failed
