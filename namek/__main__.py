from __future__ import annotations

import asyncio
import logging
import os

import discord
from discord.ext import commands
from discord.utils import setup_logging

from namek.core import Bot
from namek.core.settings import BASE_DIR, COG_DIRECTORIES, SETTINGS

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
    bot = Bot(intents=intents, owner_ids=SETTINGS.OWNER_IDS)

    await load_extensions(bot)

    await bot.start(SETTINGS.BOT_TOKEN.get_secret_value())


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
    asyncio.run(main())
