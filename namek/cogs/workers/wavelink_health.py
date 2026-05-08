from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from disckit.cogs import BaseCog
from discord.ext import commands

from namek.core import Bot

if TYPE_CHECKING:
    from wavelink import NodeDisconnectedEventPayload, NodeReadyEventPayload

_logger = logging.getLogger(__name__)


class WavelinkHealth(BaseCog, name="Wavelink Health"):
    def __init__(self, bot: Bot) -> None:
        super().__init__(logger=_logger)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(
        self, payload: NodeReadyEventPayload
    ) -> None:
        _logger.info(f"Wavelink Node {payload.node.identifier} is ready")

    @commands.Cog.listener()
    async def on_wavelink_node_disconnected(
        self, payload: NodeDisconnectedEventPayload
    ) -> None:
        _logger.info(f"Node {payload.node.identifier} has disconnected.")


async def setup(bot: Bot) -> None:
    await bot.add_cog(WavelinkHealth(bot))
