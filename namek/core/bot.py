from __future__ import annotations

import asyncio
import datetime
import logging
import os
from typing import TYPE_CHECKING

import discord
import wavelink
from discord.ext import commands
from discord.utils import MISSING

from namek.cogs import CogEnums
from namek.core.settings import (
    BASE_DIR,
    COG_DIRECTORIES,
    EMOJIS,
    EMOJIS_DIR,
    SETTINGS,
)
from namek.utils.mention_tree import MentionTree

if TYPE_CHECKING:
    from collections.abc import Collection
    from pathlib import Path

    from discord import Intents
    from discord.app_commands import AppCommand


__all__ = ("Bot",)
_logger: logging.Logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    """The main singleton bot class."""

    def __init__(
        self,
        *,
        intents: Intents,
        owner_ids: None | Collection[int] = None,
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
        self.last_reconnect: datetime.datetime = MISSING

    async def _sync_handle(self) -> None:
        _logger.info("Syncing application commands.")

        global_synced = await self.tree.sync()
        _logger.info(
            "Successfully synced %s global commands.",
            len(global_synced),
        )

        if SETTINGS.DEV_GUILD_ID is not None:
            guild_synced = await self.tree.sync(
                guild=discord.Object(SETTINGS.DEV_GUILD_ID),
            )
            _logger.info(
                "Successfully synced %s dev commands.",
                len(guild_synced),
            )

    async def init_commands_sync(self, *, force_sync: bool) -> None:
        """
        Syncs the command tree of the bot.
        This method checks if the dev commands are synced to the dev guild
        or if none of the bot commands are registerd.

        Parameters
        ----------
        force_sync : bool
            Forcibly syncs the command tree of the bot.

        """
        for cog in CogEnums:
            if cog == CogEnums.DEV_COG and SETTINGS.DEV_GUILD_ID is not None:
                self.tree.remove_command(
                    cog, guild=discord.Object(SETTINGS.DEV_GUILD_ID)
                )
            else:
                self.tree.remove_command(cog)

        if force_sync:
            _logger.info("Force syncing enabled.")
            await self._sync_handle()
            return

        app_commands: list[AppCommand] = await self.tree.fetch_commands()
        if not app_commands:
            _logger.info("No registered commands found.")
            await self._sync_handle()
            return

        dev_cog = self.get_cog(CogEnums.DEV_COG)
        if dev_cog is None:
            _logger.warning('Could not find cog: "%s"', CogEnums.DEV_COG)
            _logger.warning(
                "You will not be able to sync or manage commands without this cog.",
            )
            return

        if SETTINGS.DEV_GUILD_ID is not None:
            dev_app_commands: list[AppCommand] = await self.tree.fetch_commands(
                guild=discord.Object(SETTINGS.DEV_GUILD_ID),
            )
            found_sync = any(command.name == "dev" for command in dev_app_commands)
            if not found_sync:
                _logger.info("Sync registered command not found.")
                await self._sync_handle()
                return

    async def init_extensions(
        self,
        *,
        cogs_dir: list[Path],
        base_dir: Path,
    ) -> None:
        """
        Loads the cog extensions into the bot.

        Parameters
        ----------
        cog_dir : list[Path]
            The directories containing extension files.
        base_dir : Path
            The base path of the bot running from.

        """
        cogs_loaded = 0
        cogs_failed = 0

        for directory in cogs_dir:
            if not directory.exists():
                _logger.warning("Directory not found: %s", directory)
                continue

            for python_file in directory.rglob("*.py"):
                if python_file.name.startswith("_"):
                    continue

                relative_path = python_file.relative_to(base_dir.parent)
                module_name = str(relative_path).replace(os.sep, ".").replace(".py", "")

                if SETTINGS.DEV_GUILD_ID is None and "commands.dev" in module_name:
                    _logger.warning(
                        "DEV_GUILD_ID env variable is not set. Not loading extension: %s",
                        module_name,
                    )
                    continue

                try:
                    await self.load_extension(module_name)
                    cogs_loaded += 1
                except commands.ExtensionAlreadyLoaded:
                    _logger.warning(f"Already loaded: {module_name}")
                except commands.ExtensionFailed as e:
                    _logger.warning(f"Failed to load {module_name}: {e}")
                    cogs_failed += 1
                except commands.NoEntryPointError:
                    _logger.warning(f"No setup() function in: {module_name}")
                    cogs_failed += 1
                except Exception as e:
                    _logger.warning(
                        f"Unexpected error loading {module_name}: {e}",
                    )
                    cogs_failed += 1

        _logger.info("Cog loading complete!")
        _logger.info("Loaded: %s | Failed: %s", cogs_loaded, cogs_failed)

    async def init_wavelink_node(
        self,
        *,
        identifier: str,
        uri: str,
        password: str,
        retries: int,
    ) -> None:
        """
        Establishes connection to lavalink nodes through wavelink.

        Parameters
        ----------
        identifier : str
            The identifier name of the node.
        uri : str
            The URI of the node to connect.
        password : str
            The password of the node.
        retries : int
            Number of retries to be made when the connection fails to establish.

        """
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

    async def init_emojis(self, *, path: Path) -> None:
        """
        Initializes the emojis into discord API.
        This method uploads the emoji images only once to the API.
        If the api already exists under the bot's portal, it fetches and reuses that instead.

        Parameters
        ----------
        path : Path
            The directory path where all the emoji images lie.

        """
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

        application_emoji_set = {emoji.name.upper() for emoji in emojis}
        local_emoji_map = {asset.stem.upper(): asset for asset in path.iterdir()}

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

            try:
                image_file = path / local_emoji_map[emoji_name]
                with image_file.open("rb") as f:
                    emoji_obj = await self.create_application_emoji(
                        name=emoji_name,
                        image=f.read(),
                    )
                    setattr(EMOJIS, emoji_name, emoji_obj)
                    _logger.info("Uploaded emoji: %s", emoji_name)
                    await asyncio.sleep(0.5)
            except (FileNotFoundError, KeyError):
                _logger.warning(
                    "Could not find image for emoji: %s",
                    emoji_name,
                )
                setattr(EMOJIS, emoji_name, "❔")
            except Exception as error:
                _logger.exception(
                    "An error occured trying to upload emoji: %s",
                    emoji_name,
                    exc_info=error,
                )
                setattr(EMOJIS, emoji_name, "❔")

        _logger.info("Finished initializing emojis.")

    async def setup_hook(self) -> None:
        await self.init_emojis(path=EMOJIS_DIR)
        await self.init_extensions(cogs_dir=COG_DIRECTORIES, base_dir=BASE_DIR)
        # We MUST load the extensions only after loading the emojis for the emojis to
        # actually be present in all the views as python loads all the files eagarly
        # (including view files) which causes the buttons to having MISSING sentinel
        # instead of the actual loaded emojis

        await self.init_commands_sync(force_sync=False)
        await self.init_wavelink_node(
            identifier=SETTINGS.LAVALINK_NAME,
            uri=SETTINGS.LAVALINK_URI.get_secret_value(),
            password=SETTINGS.LAVALINK_PASSWORD.get_secret_value(),
            retries=SETTINGS.LAVALINK_RETRIES,
        )

        name = self.user.name if self.user else "Namek Bot"
        _logger.info("Logging in as %s.", name)

    async def on_ready(self) -> None:
        self.last_reconnect = datetime.datetime.now(tz=datetime.UTC)
        _logger.info("Startup / reconnect detected.")
