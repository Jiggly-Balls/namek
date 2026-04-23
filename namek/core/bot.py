from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord
from disckit.utils import MentionTree
from discord.ext import commands

from namek.core.settings import SETTINGS

if TYPE_CHECKING:
    from collections.abc import Collection

    from discord import Intents


_logger: logging.Logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    def __init__(
        self, *, intents: Intents, owner_ids: None | Collection[int] = None
    ) -> None:
        """
        Initialize the bot instance.

        Parameters
        ----------
        intents : discord.Intents
            The intents to be used by the bot for interacting with Discord.
        """
        super().__init__(
            command_prefix="/",
            intents=intents,
            help_command=None,
            tree_cls=MentionTree,
            owner_ids=owner_ids,
            chunk_guilds_at_startup=False,
        )
        self.tree: MentionTree
    
    async def __temp_sync(self) -> None:  # pyright: ignore[reportUnusedFunction]
        synced_global = await self.tree.sync()
        synced_guild = await self.tree.sync(
            guild=discord.Object(SETTINGS.DEV_GUILD_ID)
        )

        global_cmds = len(synced_global)
        guild_cmds = len(synced_guild)
        
        _logger.info("Synced %s global commands.", global_cmds)
        _logger.info("Synced %s guild commands.", guild_cmds)

    async def setup_hook(self) -> None:
        # await self.__temp_sync()
        ...
