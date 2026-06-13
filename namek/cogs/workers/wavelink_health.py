from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from discord.ext import commands

from namek.cogs import BaseGroupCog, CogEnums

if TYPE_CHECKING:
    from wavelink import NodeDisconnectedEventPayload, NodeReadyEventPayload

    from namek.core import Bot

_logger = logging.getLogger(__name__)


class WavelinkHealth(
    BaseGroupCog,
    name=CogEnums.WAVELINK_HEALTH_COG,
    group_description="Logs info on the wavelink's connection.",
):
    """Worker cog for monitoring wavelink's connection."""

    def __init__(self, bot: Bot) -> None:
        super().__init__(logger=_logger)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(
        self,
        payload: NodeReadyEventPayload,
    ) -> None:
        _logger.info('Wavelink Node "%s" is ready', payload.node.identifier)

    @commands.Cog.listener()
    async def on_wavelink_node_disconnected(
        self,
        payload: NodeDisconnectedEventPayload,
    ) -> None:
        _logger.info(
            'Wavelink Node "%s" has disconnected.',
            payload.node.identifier,
        )


async def setup(bot: Bot) -> None:
    await bot.add_cog(WavelinkHealth(bot))
