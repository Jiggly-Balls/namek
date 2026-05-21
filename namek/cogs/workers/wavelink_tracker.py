from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from disckit.cogs import BaseCog
from disckit.utils import MainEmbed
from discord.ext import commands

from namek.backend.cache import CACHE
from namek.core import Bot

if TYPE_CHECKING:
    from discord import Embed
    from wavelink import TrackStartEventPayload, TrackEndEventPayload


_logger = logging.getLogger(__name__)


class WavelinkTracker(BaseCog, name="Wavelink Tracker"):
    def __init__(self, bot: Bot) -> None:
        super().__init__(logger=_logger)

    def _generate_embed(self, payload: TrackStartEventPayload) -> Embed:
        artist = (
            f"[{payload.track.author}]({payload.track.artist.url})"
            if payload.track.artist.url
            else payload.track.author
        )

        embed = MainEmbed(
            "Playing Music",
            f"Playing `{payload.track.title}` by " + artist,
            url=payload.track.uri,
        )
        embed.set_thumbnail(url=payload.track.artwork)
        return embed

    @commands.Cog.listener()
    async def on_wavelink_track_start(
        self, payload: TrackStartEventPayload
    ) -> None:
        if not payload.player:
            return

        vc_state = CACHE.vc_states.get(payload.player)
        if not vc_state:
            return

        embed = self._generate_embed(payload)

        if not vc_state.message:
            message = await vc_state.channel.send(embed=embed, silent=True)
            CACHE.vc_states[payload.player].message = message
            return

        await vc_state.message.delete()
        message = await vc_state.channel.send(embed=embed, silent=True)
        CACHE.vc_states[payload.player].message = message

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: TrackEndEventPayload) -> None:
        ...


async def setup(bot: Bot) -> None:
    await bot.add_cog(WavelinkTracker(bot))
