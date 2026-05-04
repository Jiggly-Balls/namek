from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

import discord
import wavelink
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

    async def connect_wavelink_node(
        self, *, identifier: str, uri: str, password: str
    ) -> None:
        node = wavelink.Node(
            identifier=identifier,
            uri=uri,
            password=password,
            retries=5,
            resume_timeout=600,
        )

        try:
            await wavelink.Pool.connect(
                nodes=[node],
                client=self,
                cache_capacity=SETTINGS.LAVALINK_TRACK_CACHE,
            )
        except wavelink.AuthorizationFailedException:
            _logger.warning(
                "Incorrect password was passed into Lavalink Node connection.",
                stack_info=True,
            )
        except wavelink.NodeException:
            _logger.warning(
                "The Lavalink Node failed to connect properly. "
                "Please check that your Lavalink version is version 4.",
                stack_info=True,
            )

        await asyncio.sleep(3)

        if node.status == wavelink.NodeStatus.CONNECTED:
            _logger.info(
                "Successfully connected to Lavalink Node: %s", node.identifier
            )
        else:
            _logger.warning(
                "Failed to connect to node: %s (Status: %s)",
                node.uri,
                node.status,
            )

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
        await self.connect_wavelink_node(
            identifier=SETTINGS.LAVALINK_NAME,
            uri=SETTINGS.LAVALINK_URI.get_secret_value(),
            password=SETTINGS.LAVALINK_PASSWORD.get_secret_value(),
        )
