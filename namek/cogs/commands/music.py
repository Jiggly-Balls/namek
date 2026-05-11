import logging
from typing import cast

import discord
import wavelink
from disckit.cogs import BaseCog
from disckit.utils import ErrorEmbed, SuccessEmbed
from discord import Interaction, app_commands

from namek.core import Bot
from namek.utils.helper import safe_defer

_logger = logging.getLogger(__name__)


class MusicCog(BaseCog, name="Music Cog"):
    """
    Music Commands for the bot.

    A cog containing music-related commands for playing, controlling, and managing
    audio playback in Discord voice channels using the Wavelink library.
    """

    music_commands: app_commands.Group = app_commands.Group(
        name="music",
        description="Music related commands.",
        guild_only=True,
    )

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

    async def _vc_check(self, interaction: Interaction[Bot]) -> bool:
        assert interaction.guild
        assert isinstance(interaction.user, discord.Member)

        if not (interaction.user.voice and interaction.user.voice.channel):
            await interaction.response.send_message(
                embed=ErrorEmbed(
                    "You need to be within a voice channel to use this command."
                )
            )
            return False
        return True

    @music_commands.command()
    async def connect(self, interaction: Interaction[Bot]) -> None:
        assert isinstance(interaction.user, discord.Member)
        assert interaction.guild
        assert interaction.user.voice
        assert interaction.user.voice.channel

        in_vc = await self._vc_check(interaction)
        if not in_vc:
            return

        await interaction.response.defer()

        channel_name: str = interaction.user.voice.channel.name
        await interaction.user.voice.channel.connect()
        await interaction.followup.send(
            embed=SuccessEmbed(
                f"Successfully joined `{channel_name}` voice channel."
            )
        )

    @music_commands.command()
    async def disconnect(self, interaction: Interaction[Bot]) -> None:
        assert isinstance(interaction.user, discord.Member)
        assert interaction.guild
        assert interaction.user.voice
        assert interaction.user.voice.channel

        if interaction.guild.voice_client is None:
            await interaction.response.send_message(
                embed=ErrorEmbed("I'm not in a voice channel to disconnect.")
            )
            return

        in_vc = await self._vc_check(interaction)
        if not in_vc:
            return

        await interaction.response.defer()

        channel_name = interaction.user.voice.channel.name
        await interaction.guild.voice_client.disconnect(force=False)
        await interaction.followup.send(
            embed=SuccessEmbed(
                f"Disconnected from voice channel `{channel_name}`."
            )
        )

    @music_commands.command()
    async def play(self, interaction: Interaction[Bot], query: str) -> None:
        assert isinstance(interaction.user, discord.Member)
        assert interaction.guild

        if interaction.guild.voice_client is None:
            in_vc = await self._vc_check(interaction)
            if not in_vc:
                return

            await interaction.response.defer()

            assert interaction.user.voice
            assert interaction.user.voice.channel

            channel_name: str = interaction.user.voice.channel.name
            await interaction.user.voice.channel.connect(cls=wavelink.Player)
            await interaction.followup.send(
                embed=SuccessEmbed(
                    f"Successfully joined `{channel_name}` voice channel."
                )
            )
        
        await safe_defer(interaction)

        player: wavelink.Player = cast(
            "wavelink.Player", interaction.guild.voice_client
        )

        # Turn on AutoPlay to enabled mode.
        # enabled = AutoPlay will play songs for us and fetch recommendations...
        # partial = AutoPlay will play songs for us, but WILL NOT fetch recommendations...
        # disabled = AutoPlay will do nothing...
        player.autoplay = wavelink.AutoPlayMode.enabled

        # Lock the player to this channel...
        if not hasattr(player, "home"):
            player.home = interaction.channel
        elif player.home != interaction.channel:
            await interaction.followup.send(
                f"You can only play songs in {player.home.mention}, as the player has already started there."
            )
            return

        # This will handle fetching Tracks and Playlists...
        # Seed the doc strings for more information on this method...
        # If spotify is enabled via LavaSrc, this will automatically fetch Spotify tracks if you pass a URL...
        # Defaults to YouTube for non URL based queries...

        tracks: wavelink.Search = await wavelink.Playable.search(query)
        if not tracks:
            await interaction.followup.send(
                f"{interaction.user.mention} - Could not find any tracks with that query. Please try again."
            )
            return

        if isinstance(tracks, wavelink.Playlist):
            # tracks is a playlist...
            added: int = await player.queue.put_wait(tracks)
            await interaction.followup.send(
                f"Added the playlist **`{tracks.name}`** ({added} songs) to the queue."
            )
        else:
            track: wavelink.Playable = tracks[0]
            await player.queue.put_wait(track)
            await interaction.followup.send(f"Added **`{track}`** to the queue.")

        if not player.playing:
            # Play now since we aren't playing anything...
            await player.play(player.queue.get(), volume=30)


async def setup(bot: Bot) -> None:
    await bot.add_cog(MusicCog(bot))
