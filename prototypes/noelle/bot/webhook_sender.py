"""Helpers for sending channel messages via webhooks."""

from __future__ import annotations

import asyncio

import discord


class ChannelWebhookSender:
    """Caches one webhook per text channel for identity-preserving sends."""

    def __init__(self, bot_user_id: int) -> None:
        self._bot_user_id = bot_user_id
        self._cache: dict[int, discord.Webhook] = {}
        self._lock = asyncio.Lock()

    async def send_as_member(
        self,
        channel: discord.TextChannel,
        member: discord.Member,
        content: str,
    ) -> None:
        """Send text with the member's display name and avatar."""

        if not content.strip():
            return

        webhook = await self._get_or_create_webhook(channel)
        if webhook is None:
            # Fallback if webhook permissions are missing.
            await channel.send(f"**{member.display_name}:** {content}")
            return

        await webhook.send(
            content=content,
            username=member.display_name,
            avatar_url=member.display_avatar.url,
            allowed_mentions=discord.AllowedMentions.none(),
            wait=False,
        )

    async def _get_or_create_webhook(self, channel: discord.TextChannel) -> discord.Webhook | None:
        cached = self._cache.get(channel.id)
        if cached is not None:
            return cached

        async with self._lock:
            cached = self._cache.get(channel.id)
            if cached is not None:
                return cached

            guild_me = channel.guild.me
            if guild_me is None:
                return None

            permissions = channel.permissions_for(guild_me)
            if not permissions.manage_webhooks:
                return None

            existing = await channel.webhooks()
            webhook = next((w for w in existing if w.user and w.user.id == self._bot_user_id), None)
            if webhook is None:
                webhook = await channel.create_webhook(name="Voice Transcript Relay")

            self._cache[channel.id] = webhook
            return webhook
