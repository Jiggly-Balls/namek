from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from discord import app_commands

from namek.cogs import BaseGroupCog, CogEnums

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

async def setup(bot: Bot) -> None:
    await bot.add_cog(MiscCog(bot))
