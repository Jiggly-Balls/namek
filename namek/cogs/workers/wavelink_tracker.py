from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from disckit.cogs import BaseCog
from discord.ext import commands

from namek.core import Bot

if TYPE_CHECKING:
    from wavelink import TrackStartEventPayload


_logger = logging.getLogger(__name__)


class WavelinkTracker(BaseCog, name="Wavelink Health"):
    def __init__(self, bot: Bot) -> None:
        super().__init__(logger=_logger)

    @commands.Cog.listener()
    async def on_wavelink_track_start(
        self, payload: TrackStartEventPayload
    ) -> None: ...
