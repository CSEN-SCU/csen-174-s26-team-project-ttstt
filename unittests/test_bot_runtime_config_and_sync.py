from __future__ import annotations

import asyncio
import importlib
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _load_bot_config_loader():
    module = importlib.import_module("apps.bot.config")
    return module.load_bot_config


def _load_sync_app_commands():
    # Loaded from the dedicated module so the test does not require
    # discord.py to be installed in the test environment.
    module = importlib.import_module("apps.bot.command_sync")
    return module.sync_app_commands


def _set_required_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DISCORD_TOKEN", "abc123")
    monkeypatch.setenv("ELEVENLABS_API_KEY", "el-key")
    monkeypatch.setenv("ELEVENLABS_VOICE_ID", "voice-1")


def test_load_bot_config_reads_required_and_optional_values(monkeypatch: pytest.MonkeyPatch) -> None:
    _set_required_env(monkeypatch)
    monkeypatch.setenv("DISCORD_GUILD_ID", "987654321")

    load_bot_config = _load_bot_config_loader()
    config = load_bot_config()

    assert config.discord_token == "abc123"
    assert config.discord_guild_id == 987654321
    assert config.elevenlabs_api_key == "el-key"
    assert config.elevenlabs_voice_id == "voice-1"


def test_load_bot_config_raises_when_token_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    monkeypatch.delenv("DISCORD_BOT_TOKEN", raising=False)
    monkeypatch.setenv("ELEVENLABS_API_KEY", "el-key")
    monkeypatch.setenv("ELEVENLABS_VOICE_ID", "voice-1")
    monkeypatch.setenv("DISCORD_GUILD_ID", "123")

    with pytest.raises(ValueError, match="DISCORD_TOKEN"):
        load_bot_config = _load_bot_config_loader()
        load_bot_config()


def test_load_bot_config_raises_when_elevenlabs_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DISCORD_TOKEN", "abc123")
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    monkeypatch.delenv("ELEVENLABS_VOICE_ID", raising=False)

    with pytest.raises(ValueError, match="ELEVENLABS_"):
        load_bot_config = _load_bot_config_loader()
        load_bot_config()


@dataclass
class FakeTree:
    copied_to_guild: int | None = None
    synced_guild: int | None = None
    synced_global: bool = False

    def copy_global_to(self, guild: object) -> None:
        self.copied_to_guild = getattr(guild, "id")

    async def sync(self, guild: object | None = None) -> None:
        if guild is None:
            self.synced_global = True
            return
        self.synced_guild = getattr(guild, "id")


def test_sync_app_commands_guild_first() -> None:
    sync_app_commands = _load_sync_app_commands()
    tree = FakeTree()

    asyncio.run(sync_app_commands(tree, guild_id=12345))

    assert tree.copied_to_guild == 12345
    assert tree.synced_guild == 12345
    assert tree.synced_global is False


def test_sync_app_commands_global_when_no_guild() -> None:
    sync_app_commands = _load_sync_app_commands()
    tree = FakeTree()

    asyncio.run(sync_app_commands(tree, guild_id=None))

    assert tree.copied_to_guild is None
    assert tree.synced_guild is None
    assert tree.synced_global is True
