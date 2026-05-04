import logging

import discord
from disckit.cogs import BaseCog
from disckit.utils import ErrorEmbed, SuccessEmbed
from discord import Interaction, app_commands

from namek.core import Bot

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

    @music_commands.command()
    async def connect(self, interaction: Interaction[Bot]) -> None:
        assert interaction.guild
        assert isinstance(interaction.user, discord.Member)

        if not (interaction.user.voice and interaction.user.voice.channel):
            await interaction.response.send_message(
                embed=ErrorEmbed(
                    "You need to be within a voice channel to use this command."
                )
            )
            return

        await interaction.response.defer()

        channel_name = interaction.user.voice.channel.name
        await interaction.user.voice.channel.connect()
        await interaction.followup.send(
            embed=SuccessEmbed(
                f"Successfully joined `{channel_name}` voice channel."
            )
        )

    @music_commands.command()
    async def disconnect(self, interaction: Interaction[Bot]) -> None:
        assert interaction.guild
        assert isinstance(interaction.user, discord.Member)

        if interaction.guild.voice_client is None:
            await interaction.response.send_message(
                embed=ErrorEmbed("I'm not in a voice channel to disconnect.")
            )
            return
        if not (interaction.user.voice and interaction.user.voice.channel):
            await interaction.response.send_message(
                embed=ErrorEmbed(
                    "You need to be within a voice channel to use this command."
                )
            )
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
        assert interaction.guild
        assert isinstance(interaction.user, discord.Member)


async def setup(bot: Bot) -> None:
    await bot.add_cog(MusicCog(bot))
