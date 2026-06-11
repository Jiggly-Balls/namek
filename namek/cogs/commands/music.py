from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast
from urllib.parse import urlparse

import discord
import wavelink
from discord import app_commands

from namek.backend.cache import CACHE
from namek.cogs import BaseGroupCog, CogEnums
from namek.core.settings import ALLOWED_MUSIC_SOURCES, EMOJIS
from namek.utils import ErrorEmbed, MainEmbed, SuccessEmbed
from namek.utils.extras import VCState
from namek.utils.helper import safe_defer, vc_check

if TYPE_CHECKING:
    from discord import Interaction

    from namek.core import Bot


_logger = logging.getLogger(__name__)


@app_commands.guild_only()
class MusicCog(
    BaseGroupCog,
    name=CogEnums.MUSIC_COG,
    group_name="music",
    group_description="Music related commands.",
):
    """
    Music Commands for the bot.

    A cog containing music-related commands for playing, controlling, and managing
    audio playback in Discord voice channels using the Wavelink library.
    """

    def __init__(self, bot: Bot) -> None:
        """
        Initialize the MusicCommands cog.

        Parameters
        ----------
        bot : Bot
            The bot instance to which this cog is added.
        """
        super().__init__(logger=_logger)
        self.bot: Bot = bot

    @app_commands.command()
    async def connect(self, interaction: Interaction[Bot]) -> None:
        assert isinstance(interaction.user, discord.Member)
        assert interaction.guild

        channel = await vc_check(interaction)
        if not channel:
            return

        await interaction.response.defer()

        await channel.connect(cls=wavelink.Player, self_deaf=True)
        await interaction.followup.send(
            embed=SuccessEmbed(
                description=f"Successfully joined `{channel.name}` voice channel."
            )
        )

    @app_commands.command()
    async def disconnect(self, interaction: Interaction[Bot]) -> None:
        assert isinstance(interaction.user, discord.Member)
        assert interaction.guild

        if not (
            interaction.user.voice
            and interaction.user.voice.channel
            and interaction.guild.voice_client
        ):
            await interaction.response.send_message(
                embed=ErrorEmbed(
                    description="I'm not in a voice channel to disconnect."
                )
            )
            return

        channel = await vc_check(interaction)
        if not channel:
            return

        await interaction.response.defer()

        player: wavelink.Player = cast(
            "wavelink.Player", interaction.guild.voice_client
        )
        CACHE.delete_vc_state(player)

        await interaction.guild.voice_client.disconnect(force=False)
        await interaction.followup.send(
            embed=SuccessEmbed(
                description=f"Disconnected from voice channel `{channel.name}`."
            )
        )

    @app_commands.command()
    async def play(self, interaction: Interaction[Bot], query: str) -> None:
        assert isinstance(interaction.user, discord.Member)
        assert interaction.channel
        assert interaction.guild

        if interaction.guild.voice_client is None:
            channel = await vc_check(interaction)
            if not channel:
                return

            await interaction.response.defer()

            await channel.connect(cls=wavelink.Player, self_deaf=True)
            await interaction.followup.send(
                embed=SuccessEmbed(
                    description=f"Successfully joined `{channel.name}` voice channel."
                )
            )

        await safe_defer(interaction)

        player: wavelink.Player = cast(
            "wavelink.Player", interaction.guild.voice_client
        )

        player.autoplay = wavelink.AutoPlayMode.enabled

        if (
            vc_state := CACHE.vc_states.get(player)
        ) and vc_state.channel != interaction.channel:
            await interaction.followup.send(
                f"You can only play songs in {vc_state.channel.mention}, as the player has already started there."
            )
            return

        parsed_url = urlparse(query)
        if (
            parsed_url.scheme
            and parsed_url.netloc not in ALLOWED_MUSIC_SOURCES
        ):
            embed = ErrorEmbed(
                title="Error",
                description="This source is not supported. "
                "Please use YouTube, YouTube Music, Spotify, SoundCloud or Apple Music.",
            )
            await interaction.followup.send(embed=embed)
            return

        try:
            tracks: wavelink.Search = await wavelink.Playable.search(query)
        except wavelink.exceptions.LavalinkLoadException:
            await interaction.followup.send(
                embed=ErrorEmbed(
                    description="An error occured in looking up the track. "
                    "Please try again"
                )
            )
            return

        if not tracks:
            await interaction.followup.send(
                embed=ErrorEmbed(
                    description=f"{interaction.user.mention} - Could not find any tracks with that query. "
                    "Please try again."
                )
            )
            return

        if isinstance(tracks, wavelink.Playlist):
            added: int = await player.queue.put_wait(tracks)
            await interaction.followup.send(
                embed=MainEmbed(
                    description=f"Added the playlist **`{tracks.name}`** ({added} songs) to the queue."
                )
            )
        else:
            track: wavelink.Playable = tracks[0]
            await player.queue.put_wait(track)
            await interaction.followup.send(
                embed=MainEmbed(
                    description=f"Added **`{track}`** to the queue."
                )
            )

        if player not in CACHE.vc_states:
            CACHE.vc_states[player] = VCState(
                channel=cast(discord.TextChannel, interaction.channel),
                message=await interaction.original_response(),
            )

        if not player.playing:
            await player.play(player.queue.get(), volume=50)

    @app_commands.command(name="pause-toggle")
    async def pause_toggle(self, interaction: Interaction[Bot]) -> None:
        assert interaction.guild

        await interaction.response.defer(ephemeral=True)

        if interaction.guild.voice_client is None:
            await interaction.followup.send(
                embed=ErrorEmbed(
                    description="I'm not in any voice channel playing music."
                )
            )
            return

        player: wavelink.Player = cast(
            "wavelink.Player", interaction.guild.voice_client
        )

        vc_state = CACHE.vc_states.get(player)
        if vc_state is None:
            await interaction.followup.send(
                embed=ErrorEmbed(
                    description="Could not find the music state for this channel."
                    " Please try again."
                )
            )
            return

        vc_state.view.is_paused = not vc_state.view.is_paused
        await player.pause(vc_state.view.is_paused)

        emoji = EMOJIS.PLAY if vc_state.view.is_paused else EMOJIS.PAUSE
        if vc_state.view.is_paused:
            message = "Paused the current track."
        else:
            message = "Resuming the current track."

        vc_state.view.play_pause.emoji = emoji
        await vc_state.message.edit(view=vc_state.view)
        await interaction.followup.send(
            embed=MainEmbed(description=message),
            ephemeral=True,
        )


async def setup(bot: Bot) -> None:
    await bot.add_cog(MusicCog(bot))
