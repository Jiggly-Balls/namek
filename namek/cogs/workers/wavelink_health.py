import logging

import wavelink
from disckit.cogs import BaseCog
from discord.ext import commands

from namek.core import Bot

_logger = logging.getLogger(__name__)


class WavelinkHealth(BaseCog, name="Wavelink Health"):
    def __init__(self, bot: Bot) -> None:
        super().__init__(logger=_logger)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(
        self, payload: wavelink.NodeReadyEventPayload
    ) -> None:
        _logger.info(f"Wavelink Node {payload.node.identifier} is ready")

    @commands.Cog.listener()
    async def on_wavelink_node_disconnected(
        self, payload: wavelink.NodeDisconnectedEventPayload
    ) -> None:
        _logger.info(
            f"Node {payload.node.identifier} has disconnected. After {payload.node._retries=}"  # pyright: ignore[reportPrivateUsage]
        )


async def setup(bot: Bot) -> None:
    await bot.add_cog(WavelinkHealth(bot))
