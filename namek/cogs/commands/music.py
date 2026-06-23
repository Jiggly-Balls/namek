from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast
from urllib.parse import urlparse

import discord
import wavelink
from discord import app_commands

from namek.cogs import BaseGroupCog, CogEnums
from namek.core.settings import (
    EMOJIS,
)
from namek.core.views.music_views import QueueListPaginator
from namek.utils import ErrorEmbed, MainEmbed, SuccessEmbed
from namek.utils.extras import NamekPlayer
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
        """
        Connects to the voice channel you're present in.

        Parameters
        ----------
        interaction : Interaction[Bot]
            The discord interaction object.

        """
        interaction_channel = cast("discord.TextChannel", interaction.channel)

        channel = await vc_check(interaction)
        if not channel:
            return

        await interaction.response.defer()

        player = await channel.connect(cls=NamekPlayer, self_deaf=True)
        player.home_channel = interaction_channel
        await interaction.followup.send(
            embed=SuccessEmbed(
                description=f"Successfully joined `{channel.name}` voice channel.",
            ),
        )

    @app_commands.command()
    async def disconnect(self, interaction: Interaction[Bot]) -> None:
        """
        Disconnects from the voice channel you're present in.

        Parameters
        ----------
        interaction : Interaction[Bot]
            The discord interaction object.

        """
        interaction_guild = cast("discord.Guild", interaction.guild)

        if not interaction_guild.voice_client:
            await interaction.response.send_message(
                embed=ErrorEmbed(
                    description="I'm not in a voice channel to disconnect.",
                ),
            )
            return

        channel = await vc_check(interaction)
        if not channel:
            return

        await interaction.response.defer()

        await interaction_guild.voice_client.disconnect(force=False)
        await interaction.followup.send(
            embed=SuccessEmbed(
                description=f"Disconnected from voice channel `{channel.name}`.",
            ),
        )

    @app_commands.command()
    async def play(self, interaction: Interaction[Bot], query: str) -> None:
        """
        Play a song with the given query.

        Searches for and plays music from sources such as YouTube, Soundcloud, Bandcamp and Twitch.
        Supports both individual tracks and playlists.

        Parameters
        ----------
        interaction : Interaction[Bot]
            The discord interaction object.
        query : str
            The search query or URL to play.

        """
        interaction_guild = cast("discord.Guild", interaction.guild)
        interaction_channel = cast("discord.TextChannel", interaction.channel)
        interaction_user = cast("discord.Member", interaction.user)

        if interaction_guild.voice_client is None:
            channel = await vc_check(interaction)
            if not channel:
                return

            await interaction.response.defer()

            player = await channel.connect(cls=NamekPlayer, self_deaf=True)
            await interaction.followup.send(
                embed=SuccessEmbed(
                    description=f"Successfully joined `{channel.name}` voice channel.",
                ),
            )
            player.home_channel = interaction_channel

        voice_client = cast("discord.VoiceProtocol", interaction_guild.voice_client)
        voice_client_channel = cast("discord.VoiceChannel", voice_client.channel)
        interaction_user_voice = cast("discord.VoiceState", interaction_user.voice)
        interaction_user_voice_channel = cast(
            "discord.VoiceChannel", interaction_user_voice.channel
        )

        if voice_client_channel.id != interaction_user_voice_channel.id:
            await interaction.followup.send(
                embed=ErrorEmbed(
                    description="You need to be in the same voice channel as the bot to use this command.",
                ),
                ephemeral=True,
            )
            return

        await safe_defer(interaction)

        player_instance = cast(
            "None | NamekPlayer",
            interaction_guild.voice_client,
        )

        if player_instance is None:
            await interaction.followup.send(
                embed=ErrorEmbed(
                    title="Sorry :(",
                    description="An unexpected error occured. Please try again.",
                )
            )
            return

        if player_instance.home_channel != interaction.channel:
            await interaction.followup.send(
                embed=ErrorEmbed(
                    desciption=f"You can only play songs in {player_instance.home_channel.mention},"
                    " as the player has already started there."
                ),
                ephemeral=True,
            )
            return

        player_instance.autoplay = wavelink.AutoPlayMode.enabled

        parsed_url = urlparse(query)
        if parsed_url.scheme and parsed_url.netloc not in self.bot.available_netloc:
            titles = (
                string.title() for string in self.bot.available_streaming_sources[:-1]
            )
            sources = (
                ", ".join(titles)
                + f" or {self.bot.available_streaming_sources[-1].title()}"
            )
            embed = ErrorEmbed(
                description=f"This source is not supported. Please use {sources}.",
            )
            await interaction.followup.send(embed=embed)
            return

        try:
            tracks = await wavelink.Playable.search(query)
        except wavelink.exceptions.LavalinkLoadException:
            await interaction.followup.send(
                embed=ErrorEmbed(
                    description="An error occured in looking up the track. "
                    "Please try again.",
                ),
            )
            return

        if not tracks:
            await interaction.followup.send(
                embed=ErrorEmbed(
                    description=f"{interaction.user.mention} - Could not find any tracks with that query. "
                    "Please try again.",
                ),
            )
            return

        if isinstance(tracks, wavelink.Playlist):
            added: int = await player_instance.queue.put_wait(tracks)
            await interaction.followup.send(
                embed=MainEmbed(
                    description=f"Added the playlist **`{tracks.name}`** ({added} songs) to the queue.",
                ),
            )
        else:
            track: wavelink.Playable = tracks[0]
            await player_instance.queue.put_wait(track)
            await interaction.followup.send(
                embed=MainEmbed(
                    description=f"Added **`{track}`** to the queue.",
                ),
            )

        if not player_instance.playing:
            await player_instance.play(player_instance.queue.get(), volume=50)

    @app_commands.command(name="pause-toggle")
    async def pause_toggle(self, interaction: Interaction[Bot]) -> None:
        """
        Toggles between playing and pausing the track from your current session.

        Parameters
        ----------
        interaction : Interaction[Bot]
            The discord interaction object.

        """
        interaction_guild = cast("discord.Guild", interaction.guild)

        await interaction.response.defer(ephemeral=True)

        if interaction_guild.voice_client is None:
            await interaction.followup.send(
                embed=ErrorEmbed(
                    description="I'm not in any voice channel playing music.",
                ),
            )
            return

        player = cast(
            "None | NamekPlayer",
            interaction_guild.voice_client,
        )

        if player is None:
            await interaction.followup.send(
                embed=ErrorEmbed(
                    description="Could not find the music state for this channel."
                    " Please try again.",
                ),
            )
            return

        player.song_view.is_paused = not player.song_view.is_paused
        await player.pause(player.song_view.is_paused)

        emoji = EMOJIS.PLAY if player.song_view.is_paused else EMOJIS.PAUSE
        if player.song_view.is_paused:
            message = "Paused the current track."
        else:
            message = "Resuming the current track."

        player.song_view.play_pause.emoji = emoji
        await player.song_message.edit(view=player.song_view)
        await interaction.followup.send(
            embed=MainEmbed(description=message),
            ephemeral=True,
        )

    @app_commands.command()
    async def queue(self, interaction: Interaction[Bot]) -> None:
        """
        Show the list of all queued songs.

        Parameters
        ----------
        interaction : Interaction[Bot]
            The discord interaction object.

        """
        interaction_guild = cast("discord.Guild", interaction.guild)

        player = cast("NamekPlayer | None", interaction_guild.voice_client)
        if player is None:
            embed = ErrorEmbed(description="I'm not playing any music currently.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if not player.queue:
            embed = MainEmbed(description="The queue is currently empty.")
            await interaction.response.send_message(embed=embed)
            return

        await interaction.response.defer()

        original_response = await interaction.original_response()
        song_pages: list[str] = []

        for index, track in enumerate(player.queue, start=1):
            if track.uri:
                song = f"### `{index}.` [{track.title}]({track.uri})\n— _{track.author}_"
            else:
                song = f"### `{index}.` {track.title}\n— _{track.author}_"
            song_pages.append(song)

        paginator = QueueListPaginator(
            interaction=interaction,
            original_response=original_response,
            author=interaction.user.id,
            songs=song_pages,
            items_per_page=7,
        )
        await paginator.start()


async def setup(bot: Bot) -> None:
    await bot.add_cog(MusicCog(bot))
