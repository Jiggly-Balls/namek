from __future__ import annotations

import asyncio
import logging
import os
from typing import TYPE_CHECKING

import disckit
import discord
import wavelink
from disckit import UtilConfig
from disckit.cogs import dis_load_extension
from discord.ext import commands
from discord.utils import setup_logging

from namek.core import Bot
from namek.core.settings import BASE_DIR, COG_DIRECTORIES, SETTINGS

if TYPE_CHECKING:
    from typing import Any


logging.basicConfig(
    filename="bot.log",
    filemode="w",
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
)

logging.getLogger("discord").setLevel(logging.WARNING)
setup_logging()

_logger: logging.Logger = logging.getLogger(__name__)


async def main() -> None:
    intents = discord.Intents(guilds=True, members=True, voice_states=True)

    UtilConfig.BUG_REPORT_CHANNEL = SETTINGS.BUG_REPORT_CHANNEL_ID
    UtilConfig.STATUS_FUNC = (status_handler, ())
    UtilConfig.STATUS_TYPE = discord.ActivityType.listening
    UtilConfig.STATUS_COOLDOWN = 600

    try:
        bot = Bot(intents=intents, owner_ids=SETTINGS.OWNER_IDS)

        await load_extensions(bot)
        await dis_load_extension(
            bot,
            disckit.CogEnum.ERROR_HANDLER,
            disckit.CogEnum.STATUS_HANDLER,
            disckit.CogEnum.HELP_COG,
        )

        await bot.start(SETTINGS.BOT_TOKEN.get_secret_value())
    finally:
        await wavelink.Pool.close()


async def status_handler(bot: Bot, *args: Any) -> tuple[str, ...]:
    # Prefixed by "Listening to" from the activity type.
    return ("Listening to humans.", "Listening to your horrible music taste.")


async def load_extensions(bot: Bot) -> None:
    cogs_loaded = 0
    cogs_failed = 0

    for directory in COG_DIRECTORIES:
        if not directory.exists():
            _logger.warning("Directory not found: %s", directory)
            continue

        _logger.info("Loading cogs from: %s", directory.relative_to(BASE_DIR))

        for python_file in directory.rglob("*.py"):
            if python_file.name.startswith("_"):
                continue

            relative_path = python_file.relative_to(BASE_DIR)
            module_name = (
                str(relative_path).replace(os.sep, ".").replace(".py", "")
            )

            try:
                await bot.load_extension(module_name)
                _logger.info(f"Loaded: {module_name}")
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
                _logger.warning(f"Unexpected error loading {module_name}: {e}")
                cogs_failed += 1

    _logger.info("Cog loading complete!")
    _logger.info("Loaded: %s | Failed: %s", cogs_loaded, cogs_failed)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _logger.info("Exited due to Keyboard Interrupt.")
