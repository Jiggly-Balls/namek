from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

import disckit
import discord
import wavelink
from disckit import UtilConfig
from disckit.cogs import dis_load_extension
from discord.utils import setup_logging

from namek.core import Bot
from namek.core.settings import SETTINGS

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

        await dis_load_extension(
            bot,
            disckit.CogEnum.ERROR_HANDLER,
            disckit.CogEnum.STATUS_HANDLER,
        )

        await bot.start(SETTINGS.BOT_TOKEN.get_secret_value())
    finally:
        await wavelink.Pool.close()


async def status_handler(bot: Bot, *args: Any) -> tuple[str, ...]:
    # Prefixed by "Listening to" from the activity type.
    return ("Listening to humans.", "Listening to your horrible music taste.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        _logger.info("Exited due to Keyboard Interrupt.")
