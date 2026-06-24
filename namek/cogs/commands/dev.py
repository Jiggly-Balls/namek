from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast

import discord
import wavelink
from discord import app_commands

from namek.cogs import BaseGroupCog, CogEnums
from namek.core.settings import SETTINGS
from namek.utils import MainEmbed
from namek.utils.helper import owner_only

if TYPE_CHECKING:
    from discord import Interaction

    from namek.core import Bot


_logger = logging.getLogger(__name__)
DEV_GUILD_ID: int = cast("int", SETTINGS.DEV_GUILD_ID)


@app_commands.guild_only()
@app_commands.guilds(DEV_GUILD_ID)
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
    @owner_only()
    async def sync(self, interaction: Interaction[Bot]) -> None:
        """
        Developer command to sync the bot's slash commands with discord.

        Parameters
        ----------
        interaction : Interaction[Bot]
            The discord interaction object.

        """
        await interaction.response.defer()

        global_synced = await self.bot.tree.sync()
        guild_synced = await self.bot.tree.sync(
            guild=discord.Object(DEV_GUILD_ID),
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

    @app_commands.command(name="wavelink-reconnect")
    @owner_only()
    async def wavelink_reconnect(self, interaction: Interaction[Bot]) -> None:
        """
        If the wavelink nodes are facing issue, you can manually reconnect them via this command.

        Parameters
        ----------
        interaction : Interaction[Bot]
            The discord interaction object.

        """
        await interaction.response.defer()

        _logger.info("Initiating wavelink node reconnect by %s", interaction.user.name)

        try:
            node = wavelink.Pool.get_node()
            await node.close(eject=True)
        except wavelink.InvalidNodeException:
            pass
        finally:
            await self.bot.init_wavelink_node(
                identifier=SETTINGS.LAVALINK_NAME,
                uri=SETTINGS.LAVALINK_URI.get_secret_value(),
                password=SETTINGS.LAVALINK_PASSWORD.get_secret_value(),
                retries=SETTINGS.LAVALINK_RETRIES,
            )

        _logger.info("Finished wavelink node reconnect.")

        await interaction.followup.send(
            embed=MainEmbed(description="Successfully reconnected wavelink node.")
        )


async def setup(bot: Bot) -> None:
    await bot.add_cog(DevCog(bot))
