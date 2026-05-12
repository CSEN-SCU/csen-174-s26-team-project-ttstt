from __future__ import annotations

from apps.bot.main import _should_enqueue_message


def test_should_enqueue_message_requires_control_channel_and_listened_user() -> None:
    assert _should_enqueue_message(
        control_channel_id=10,
        message_channel_id=10,
        author_is_bot=False,
        guild_present=True,
        is_listened_user=True,
    )
    assert not _should_enqueue_message(
        control_channel_id=10,
        message_channel_id=20,
        author_is_bot=False,
        guild_present=True,
        is_listened_user=True,
    )
    assert not _should_enqueue_message(
        control_channel_id=10,
        message_channel_id=10,
        author_is_bot=False,
        guild_present=True,
        is_listened_user=False,
    )
    assert not _should_enqueue_message(
        control_channel_id=10,
        message_channel_id=10,
        author_is_bot=True,
        guild_present=True,
        is_listened_user=True,
    )
