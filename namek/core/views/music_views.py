from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import ButtonStyle

from namek.backend.cache import CACHE
from namek.core.settings import EMOJIS
from namek.core.views import BaseLayoutView
from namek.utils import ErrorEmbed, MainEmbed
from namek.utils.helper import vc_check

if TYPE_CHECKING:
    from typing import Any

    from discord import File, Interaction
    from discord.ui import ActionRow, Button, Container
    from wavelink import Player

    from namek.core import Bot


__all__ = ("PlayLayoutView",)


class PlayLayoutView(BaseLayoutView):
    container: Container["PlayLayoutView"] = discord.ui.Container()
    row1: ActionRow["PlayLayoutView"] = discord.ui.ActionRow()
    row2: ActionRow["PlayLayoutView"] = discord.ui.ActionRow()

    def __init__(
        self,
        player: Player,
        song_title: str,
        song_author: str,
        duration: str,
        media_file: File,
        thumbnail_url: None | str,
    ) -> None:
        super().__init__(timeout=None)

        self.player: Player = player
        self.is_paused: bool = False

        _section_kwargs: dict[str, Any] = {}
        if thumbnail_url:
            _section_kwargs["accessory"] = discord.ui.Thumbnail[
                "PlayLayoutView"
            ](media=thumbnail_url)

        title_section = discord.ui.Section["PlayLayoutView"](
            discord.ui.TextDisplay(
                content=f"## {song_title}\n**  **—{song_author}",
            ),
            **_section_kwargs,
        )
        media_section = discord.ui.MediaGallery["PlayLayoutView"](
            discord.MediaGalleryItem(media=media_file),
        )

        self.container.add_item(title_section)
        self.container.add_item(media_section)

    async def interaction_check(self, interaction: Interaction[Bot]) -> bool:
        channel = await vc_check(interaction)
        if channel is None:
            return False
        return True

    @row1.button(label="\u200b", style=ButtonStyle.grey, disabled=True)
    async def dud_button_1(
        self,
        interaction: Interaction[Bot],
        button: Button["PlayLayoutView"],
    ) -> None: ...

    @row1.button(emoji=EMOJIS.PREVIOUS, style=ButtonStyle.blurple)
    async def previous_callback(
        self,
        interaction: Interaction[Bot],
        button: Button["PlayLayoutView"],
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

    @row1.button(emoji=EMOJIS.DISCONNECT, style=ButtonStyle.red)
    async def delete_callback(
        self,
        interaction: Interaction[Bot],
        button: Button["PlayLayoutView"],
    ) -> None:
        await interaction.response.defer()

        channel = await vc_check(interaction)
        if not channel or not interaction.message:
            return

        assert interaction.guild
        assert interaction.guild.voice_client

        vc_state = CACHE.vc_states.get(self.player)
        if vc_state is None:
            await interaction.followup.send(
                embed=ErrorEmbed(
                    description="The player has already disconnected.",
                ),
                ephemeral=True,
            )
            return

        await vc_state.message.delete()

        await self.player.pause(True)
        CACHE.delete_vc_state(self.player)
        await interaction.guild.voice_client.disconnect(force=False)

        await interaction.followup.send(
            embed=MainEmbed(
                description=f"Disconnected from voice channel `{channel.name}`",
            ),
        )
        self.stop()

    @row1.button(emoji=EMOJIS.NEXT, style=ButtonStyle.blurple)
    async def next_callback(
        self,
        interaction: Interaction[Bot],
        button: Button["PlayLayoutView"],
    ) -> None:
        await interaction.response.defer(ephemeral=True)

        await self.player.skip(force=True)
        current_song = self.player.current
        if not current_song:
            return

        await interaction.followup.send(
            embed=MainEmbed(
                description=f"Skipped current song. Now playing `{current_song.title}`",
            ),
            ephemeral=True,
        )

    @row1.button(label="\u200b", style=ButtonStyle.grey, disabled=True)
    async def dud_button_2(
        self,
        interaction: Interaction[Bot],
        button: Button["PlayLayoutView"],
    ) -> None: ...

    @row2.button(label="\u200b", style=ButtonStyle.grey, disabled=True)
    async def dud_button_3(
        self,
        interaction: Interaction[Bot],
        button: Button["PlayLayoutView"],
    ) -> None: ...

    @row2.button(label="\u200b", style=ButtonStyle.grey, disabled=True)
    async def dud_button_4(
        self,
        interaction: Interaction[Bot],
        button: Button["PlayLayoutView"],
    ) -> None: ...

    @row2.button(emoji=EMOJIS.PAUSE, style=ButtonStyle.green)
    async def play_pause(
        self,
        interaction: Interaction[Bot],
        button: Button["PlayLayoutView"],
    ) -> None:
        await interaction.response.defer(ephemeral=True)

        self.is_paused = not self.is_paused
        await self.player.pause(self.is_paused)

        if interaction.message:
            button.emoji = EMOJIS.PLAY if self.is_paused else EMOJIS.PAUSE
            await interaction.followup.edit_message(
                interaction.message.id,
                view=self,
            )
        if self.is_paused:
            message = "Paused the current track."
        else:
            message = "Resuming the current track."

        await interaction.followup.send(
            embed=MainEmbed(description=message),
            ephemeral=True,
        )

    @row2.button(label="\u200b", style=ButtonStyle.grey, disabled=True)
    async def dud_button_5(
        self,
        interaction: Interaction[Bot],
        button: Button["PlayLayoutView"],
    ) -> None: ...

    @row2.button(label="\u200b", style=ButtonStyle.grey, disabled=True)
    async def dud_button_6(
        self,
        interaction: Interaction[Bot],
        button: Button["PlayLayoutView"],
    ) -> None: ...
