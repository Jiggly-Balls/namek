from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord
from discord import app_commands

from namek.cogs import BaseGroupCog, CogEnums
from namek.utils import MainEmbed

if TYPE_CHECKING:
    from discord import Interaction

    from namek.core import Bot


_logger = logging.getLogger(__name__)


@app_commands.guild_only()
class MiscCog(
    BaseGroupCog,
    name=CogEnums.MISC_COG,
    group_name="misc",
    group_description="Miscellaneous commands about the bot.",
):
    """
    Miscellaneous Commands for the bot.

    This cog contains commands related to bot status, information, etc.
    """

    def __init__(self, bot: Bot) -> None:
        super().__init__(logger=_logger)

        self.bot: Bot = bot

    @app_commands.command()
    async def status(self, interaction: Interaction[Bot]) -> None:
        """
        Show the bot's status, including uptime, latency, and database status.

        Parameters
        ----------
        interaction : Interaction[Bot]
            The discord interaction object.

        """
        await interaction.response.defer()

        last_reconnect_relative = (
            f"{discord.utils.format_dt(self.bot.last_reconnect, style='R')}"
        )
        latency = round(self.bot.latency * 1000)

        app_info = await self.bot.application_info()
        guild_count = app_info.approximate_guild_count
        user_count = len(self.bot.users)

        if app_info.approximate_user_install_count:
            user_count += app_info.approximate_user_install_count

        description = (
            f"**Bot Latency:       **`{latency}`ms\n"
            f"**Last Reconnect:    **{last_reconnect_relative}\n\n"
            f"**Total Guild Count: **`{guild_count}`\n"
            f"**Total User Count:  **`{user_count}`"
        )

        await interaction.followup.send(
            embed=MainEmbed(
                title="Namek Status",
                description=description,
            )
        )


async def setup(bot: Bot) -> None:
    await bot.add_cog(MiscCog(bot))
