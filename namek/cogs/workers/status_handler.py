from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord
from discord.ext import tasks
from discord.utils import MISSING

from namek.cogs import BaseGroupCog, CogEnums
from namek.core.settings import STATUS_COOLDOWN

if TYPE_CHECKING:
    from collections.abc import Iterator

    from namek.core import Bot


_logger = logging.getLogger(__name__)


class StatusHandler(
    BaseGroupCog,
    name=CogEnums.STATUS_HANDLER_COG,
    group_description="Handles the bot's status.",
):
    """Cog for handling bot's dynamic status."""

    def __init__(self, bot: Bot) -> None:
        super().__init__(_logger)
        self.bot: Bot = bot
        self.status: Iterator[str] = MISSING

    async def cog_load(self) -> None:
        self.status_task.start()
        await super().cog_load()

    async def cog_unload(self) -> None:
        self.status_task.cancel()
        await super().cog_unload()

    @tasks.loop(seconds=STATUS_COOLDOWN)
    async def status_task(self) -> None:
        await self.bot.wait_until_ready()

        if self.status is MISSING:
            self.status = await self._get_status_iter()

        try:
            current_status = next(self.status)
        except StopIteration:
            self.status = await self._get_status_iter()
            current_status = next(self.status)

        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.playing, name=current_status
            )
        )

    async def _get_status_iter(self) -> Iterator[str]:
        total_users = len(self.bot.users)
        total_guilds = len(self.bot.guilds)

        statuses: tuple[str, ...] = (
            "Listening to your horrible music taste",
            f"Listening to {total_users:,} humans across {total_guilds:,} servers.",
            "Beep boop.",
        )

        return iter(statuses)


async def setup(bot: Bot) -> None:
    await bot.add_cog(StatusHandler(bot))
