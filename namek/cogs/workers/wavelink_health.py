from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import wavelink
from discord.ext import commands

from namek.cogs import BaseGroupCog, CogEnums
from namek.core.settings import STREAM_SOURCES

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

        self.bot: Bot = bot

    @commands.Cog.listener()
    async def on_wavelink_node_ready(
        self,
        payload: NodeReadyEventPayload,
    ) -> None:
        _logger.info('Wavelink Node "%s" is ready', payload.node.identifier)

        try:
            connected_node = wavelink.Pool.get_node()
        except wavelink.InvalidNodeException:
            _logger.warning("Could not fetch any nodes")
            return

        try:
            node_info = await connected_node.fetch_info()
        except wavelink.LavalinkException as error:
            _logger.warning(
                "[STATUS CODE %s] Could not fetch node info. Reason: %s",
                error.status,
                error.error,
            )
            return
        except wavelink.NodeException as error:
            _logger.warning(
                "An error occured while making this request to Lavalink. Returned with status code: %s",
                error.status,
            )
            return

        self.bot.available_streaming_sources = node_info.source_managers
        self.bot.available_streaming_sources.remove("http")
        for source in self.bot.available_streaming_sources:
            self.bot.available_netloc.extend(STREAM_SOURCES[source])

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
