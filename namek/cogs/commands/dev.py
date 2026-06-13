from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord
from discord import app_commands

from namek.cogs import BaseGroupCog, CogEnums
from namek.core.settings import SETTINGS
from namek.utils import MainEmbed

if TYPE_CHECKING:
    from discord import Interaction

    from namek.core import Bot


_logger = logging.getLogger(__name__)


@app_commands.guild_only()
@app_commands.guilds(SETTINGS.DEV_GUILD_ID)
class DevCog(
    BaseGroupCog,
    name=CogEnums.DEV_COG,
    group_name="dev",
    group_description="Developer related commands.",
):
    """
    Developer Commands for the bot.

    This cog contains commands to be used for developing / testing.
    """

    def __init__(self, bot: Bot) -> None:
        super().__init__(logger=_logger)

        self.bot: Bot = bot

    @app_commands.command()
    async def sync(self, interaction: Interaction[Bot]) -> None:
        """Developer command to sync the bot's slash commands with discord."""

        await interaction.response.defer()

        global_synced = await self.bot.tree.sync()
        guild_synced = await self.bot.tree.sync(
            guild=discord.Object(SETTINGS.DEV_GUILD_ID),
        )

        _logger.info(
            "Syncing bot commands via sync command. Executed by %s",
            interaction.user.name,
        )
        _logger.info(
            "Successfully synced %s global commands.",
            len(global_synced),
        )
        _logger.info(
            "Successfully synced %s dev commands.",
            len(guild_synced),
        )

        await interaction.followup.send(
            embed=MainEmbed(
                title="Command Synchronization",
                description=f"Successfully synced `{len(global_synced)}` global commands "
                f"and `{len(guild_synced)}` dev commands. Restart your discord if you don't"
                " see the changes.",
            ),
        )


async def setup(bot: Bot) -> None:
    await bot.add_cog(DevCog(bot))
