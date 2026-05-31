from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import ButtonStyle
from discord.ui import Button

from namek.backend.cache import CACHE
from namek.core.settings import EMOJIS
from namek.core.views import BaseView
from namek.utils import ErrorEmbed, MainEmbed
from namek.utils.helper import vc_check

if TYPE_CHECKING:
    from discord import Interaction
    from wavelink import Player

    from namek.core import Bot


__all__ = ("PlayView",)


class PlayView(BaseView):
    def __init__(self, player: Player) -> None:
        super().__init__(timeout=None)

        self.player: Player = player
        self.is_pause: bool = False

    async def interaction_check(self, interaction: Interaction[Bot]) -> bool:
        channel = await vc_check(interaction)
        if channel is None:
            return False
        return True

    @discord.ui.button(label="\u200b", style=ButtonStyle.grey, disabled=True)
    async def dud_button_1(
        self, interaction: Interaction[Bot], button: Button["PlayView"]
    ) -> None: ...

    @discord.ui.button(emoji=EMOJIS.PREVIOUS, style=ButtonStyle.blurple)
    async def previous_callback(
        self, interaction: Interaction[Bot], button: Button["PlayView"]
    ) -> None:
        await interaction.response.defer(ephemeral=True)

        await vc_check(interaction)

        if self.player.queue.history and len(self.player.queue.history) > 1:
            current_track = self.player.current
            if current_track:
                self.player.queue.put_at(0, current_track)

            previous_track = self.player.queue.history.get_at(-2)
            await self.player.play(previous_track)

            embed = MainEmbed(
                title="Track Rewinded",
                description=f"Rewinded to: **{previous_track}**",
            )
        else:
            embed = ErrorEmbed(
                title="Error",
                description="No previous track found in the history.",
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

    @discord.ui.button(emoji=EMOJIS.DISCONNECT, style=ButtonStyle.red)
    async def delete_callback(
        self, interaction: Interaction[Bot], button: Button["PlayView"]
    ) -> None:
        await interaction.response.defer()

        channel = await vc_check(interaction)
        if not channel or not interaction.message:
            return

        assert interaction.guild
        assert interaction.guild.voice_client

        await self.player.pause(True)
        CACHE.delete_vc_state(self.player)
        await interaction.guild.voice_client.disconnect(force=False)

        await interaction.followup.edit_message(
            interaction.message.id,
            embed=MainEmbed(
                description=f"Disconnected from voice channel `{channel.name}`"
            ),
            view=None,
        )
        self.stop()

    @discord.ui.button(emoji=EMOJIS.NEXT, style=ButtonStyle.blurple)
    async def next_callback(
        self, interaction: Interaction[Bot], button: Button["PlayView"]
    ) -> None:
        await interaction.response.defer(ephemeral=True)

        await self.player.skip(force=True)
        current_song = self.player.current
        if not current_song:
            return

        await interaction.followup.send(
            embed=MainEmbed(
                description=f"Skipped current song. Now playing `{current_song.title}`"
            ),
            ephemeral=True,
        )

    @discord.ui.button(label="\u200b", style=ButtonStyle.grey, disabled=True)
    async def dud_button_2(
        self, interaction: Interaction[Bot], button: Button["PlayView"]
    ) -> None: ...

    @discord.ui.button(emoji=EMOJIS.PAUSE, style=ButtonStyle.green)
    async def play_pause(
        self, interaction: Interaction[Bot], button: Button["PlayView"]
    ) -> None:
        await interaction.response.defer(ephemeral=True)

        self.is_pause = not self.is_pause
        await self.player.pause(self.is_pause)

        if interaction.message:
            button.emoji = (
                f"{EMOJIS.PAUSE}" if self.is_pause else f"{EMOJIS.PLAY}"
            )
            await interaction.followup.edit_message(
                interaction.message.id, view=self
            )

        await interaction.followup.send(
            embed=MainEmbed(description="Paused the current track"),
            ephemeral=True,
        )
