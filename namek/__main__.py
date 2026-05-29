from __future__ import annotations

import asyncio
import logging

import disckit
import discord
import wavelink
from disckit import UtilConfig
from disckit.cogs import dis_load_extension
from discord.utils import setup_logging

from namek.core import Bot
from namek.core.settings import SETTINGS

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

    try:
        bot = Bot(intents=intents, owner_ids=SETTINGS.OWNER_IDS)

        await dis_load_extension(
            bot,
            disckit.CogEnum.ERROR_HANDLER,
        )

        await bot.start(SETTINGS.BOT_TOKEN.get_secret_value())
    finally:
        await wavelink.Pool.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _logger.info("Exited due to Keyboard Interrupt.")
