from __future__ import annotations

import asyncio
import logging

import discord
import wavelink
from discord.utils import setup_logging

from namek.core import Bot
from namek.core.settings import SETTINGS

logging.basicConfig(
    filename="bot.log",
    filemode="w",
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
)
logging.getLogger("googletrans").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
setup_logging()

_logger: logging.Logger = logging.getLogger(__name__)


async def main() -> None:
    intents = discord.Intents(guilds=True, members=True, voice_states=True)

    try:
        bot = Bot(intents=intents, owner_ids=SETTINGS.OWNER_IDS)
        await bot.start(SETTINGS.BOT_TOKEN.get_secret_value())
    finally:
        await wavelink.Pool.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _logger.info("Exited due to Keyboard Interrupt.")
