"""Slash-command sync helper for the Discord bot.

Kept in its own module (with no top-level ``discord`` import) so unit tests
can exercise the sync logic in environments where ``discord.py`` is not
installed (e.g. CI runs that only install ``pytest``).

discord.py's ``CommandTree`` API treats the ``guild`` parameter as a
``Snowflake`` protocol -- anything with an ``id`` attribute is accepted -- so
a small dataclass works in both production and tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class CommandTreeLike(Protocol):
    def copy_global_to(self, guild: Any) -> None: ...
    async def sync(self, guild: Any | None = None) -> Any: ...


@dataclass(frozen=True)
class _GuildRef:
    """Minimal Snowflake-compatible wrapper used to target a guild for sync."""

    id: int


async def sync_app_commands(tree: CommandTreeLike, guild_id: int | None) -> None:
    """Sync slash commands to a single guild (fast) or globally (slow)."""
    if guild_id is None:
        await tree.sync()
        return
    guild_ref = _GuildRef(id=guild_id)
    tree.copy_global_to(guild=guild_ref)
    await tree.sync(guild=guild_ref)
