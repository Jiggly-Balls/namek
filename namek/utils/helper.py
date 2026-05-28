from __future__ import annotations

from typing import TYPE_CHECKING

import discord

from namek.utils import ErrorEmbed

if TYPE_CHECKING:
    from discord import Interaction, InteractionCallbackResponse
    from discord.voice_client import VocalGuildChannel

    from namek.core import Bot


__all__ = ("safe_defer", "vc_check")


async def safe_defer(
    interaction: Interaction[Bot],
) -> None | InteractionCallbackResponse[Bot]:
    if not interaction.response.is_done():
        return await interaction.response.defer()


async def vc_check(interaction: Interaction[Bot]) -> None | VocalGuildChannel:
    assert isinstance(interaction.user, discord.Member)

    if not (interaction.user.voice and interaction.user.voice.channel):
        send_message_func = (
            interaction.followup.send
            if interaction.response.is_done()
            else interaction.response.send_message
        )

        await send_message_func(
            embed=ErrorEmbed(
                description="You need to be within a voice channel to use this command."
            )
        )
        return None
    return interaction.user.voice.channel
