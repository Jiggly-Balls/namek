from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

import discord
import wavelink
from disckit.utils import MentionTree
from discord.ext import commands
from discord.utils import MISSING

from namek.core.settings import ASSET_DIR, EMOJIS, SETTINGS

if TYPE_CHECKING:
    from collections.abc import Collection

    from discord import Intents


__all__ = ("Bot",)
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
        owner_ids : None | collections.abc.Collection[int]
            A collection of all owner IDs as integers to be passed in. This is optional.
        """
        super().__init__(
            command_prefix=MISSING,
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

    async def init_wavelink_node(
        self, *, identifier: str, uri: str, password: str, retries: int
    ) -> None:
        node = wavelink.Node(
            identifier=identifier,
            uri=uri,
            password=password,
            retries=retries,
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

    async def init_emojis(self) -> None:
        emojis = await self.fetch_application_emojis()
        for emoji in emojis:
            emoji_name = emoji.name.upper()

            default_value = getattr(EMOJIS, emoji_name, None)
            # The returned value must be `None` (attr doesn't exist) or
            # a sentinel value `discord.utils.MISSING` (attr exists).

            if default_value is None:
                _logger.warning(
                    "[0] Skipping emoji assignment: Could not find attribute `EMOJIS.%s`. "
                    "Double check the spelling in the filename and in the `_Emoji` class.",
                    emoji_name,
                )
                continue

            setattr(EMOJIS, emoji_name, emoji)

        application_emoji_set = set(emoji.name.upper() for emoji in emojis)
        local_emoji_map = {
            asset.stem.upper(): asset for asset in ASSET_DIR.iterdir()
        }

        missing_emojis = application_emoji_set ^ set(local_emoji_map)
        if not missing_emojis:
            _logger.info("All emojis are present.")
            return

        for emoji_name in missing_emojis:
            default_value = getattr(EMOJIS, emoji_name, None)
            # The returned value must be `None` (attr doesn't exist) or
            # a sentinel value `discord.utils.MISSING` (attr exists).

            if default_value is None:
                _logger.warning(
                    "[1] Skipping emoji assignment: Could not find attribute `EMOJIS.%s`. "
                    "Double check the spelling in the filename and in the `_Emoji` class.",
                    emoji_name,
                )
                continue

            with open(ASSET_DIR / local_emoji_map[emoji_name], "rb") as f:
                emoji_obj = await self.create_application_emoji(
                    name=emoji_name, image=f.read()
                )
                setattr(EMOJIS, emoji_name, emoji_obj)
                _logger.info("Uploaded emoji: %s", emoji_name)
                await asyncio.sleep(0.5)

        _logger.info("Finished initializing emojis.")

    async def setup_hook(self) -> None:
        # await self.__temp_sync()

        await self.init_wavelink_node(
            identifier=SETTINGS.LAVALINK_NAME,
            uri=SETTINGS.LAVALINK_URI.get_secret_value(),
            password=SETTINGS.LAVALINK_PASSWORD.get_secret_value(),
            retries=SETTINGS.LAVALINK_RETRIES,
        )

        await self.init_emojis()

        name = self.user.name if self.user else "Namek Bot"
        _logger.info("%s has successfully logged in.", name)
