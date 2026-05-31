from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import wavelink
from discord.ext import commands

from namek.backend.cache import CACHE
from namek.cogs import BaseGroupCog, CogEnums
from namek.core.views.music_views import PlayView
from namek.utils import MainEmbed

if TYPE_CHECKING:
    from discord import Embed
    from wavelink import TrackEndEventPayload, TrackStartEventPayload

    from namek.core import Bot


_logger = logging.getLogger(__name__)


class WavelinkTracker(
    BaseGroupCog,
    name=CogEnums.WAVELINK_TRACKER_COG,
    group_description="Tracks the songs being played.",
):
    def __init__(self, bot: Bot) -> None:
        super().__init__(logger=_logger)

    def _generate_embed(self, payload: TrackStartEventPayload) -> Embed:
        artist = (
            f"[{payload.track.author}]({payload.track.artist.url})"
            if payload.track.artist.url
            else f"`{payload.track.author}`"
        )
        title = (
            f"[{payload.track.title}]({payload.track.uri})"
            if payload.track.uri
            else f"`{payload.track.title}`"
        )

        embed = (
            MainEmbed(
                title="Playing Music",
                url=payload.track.uri,
            )
            .add_field(name="Song Name", value=title)
            .add_field(name="Artist", value=artist)
        )
        embed.set_image(url=payload.track.artwork)
        return embed

    @commands.Cog.listener()
    async def on_wavelink_track_start(
        self, payload: TrackStartEventPayload
    ) -> None:
        if payload.player is None:
            return

        vc_state = CACHE.vc_states.get(payload.player)
        if not vc_state:
            return

        embed = self._generate_embed(payload)

        if vc_state.message:
            await vc_state.message.delete()

        message = await vc_state.channel.send(
            embed=embed, view=PlayView(payload.player), silent=True
        )
        CACHE.vc_states[payload.player].message = message

    @commands.Cog.listener()
    async def on_wavelink_track_end(
        self, payload: TrackEndEventPayload
    ) -> None:
        if payload.player is None:
            return

        vc_state = CACHE.vc_states.get(payload.player)
        if not vc_state:
            return

        if not payload.player.queue and not payload.player.auto_queue:
            post_text = (
                "You can continue adding more tracks queue or "
                "listen to our fine tuned auto recommendation."
            )
            if payload.player.autoplay is wavelink.AutoPlayMode.disabled:
                post_text = (
                    "You can continue listening to more songs by adding tracks to the queue. "
                    "My autoplay is disabled. "
                    "I will leave the voice channel in a few minutes if no songs are being played."
                )

            track = (
                f"[{payload.track.title}]({payload.track.uri})"
                if payload.track.uri
                else f"**{payload.track.title}**"
            )
            artist = (
                f"[{payload.track.author}]({payload.track.artist.url})"
                if payload.track.artist.url
                else f"**{payload.track.author}**"
            )

            track_end_embed = MainEmbed(
                title="Finished playing your queue",
                description="All tracks have finished playing from this queue."
                f"\n{post_text}",
            )
            post_end_embed = (
                MainEmbed()
                .add_field(
                    name="Last played track", value=f"{track}\n\n\\- {artist}"
                )
                .set_thumbnail(url=payload.track.artwork)
            )

            await vc_state.channel.send(
                embeds=[track_end_embed, post_end_embed]
            )


async def setup(bot: Bot) -> None:
    await bot.add_cog(WavelinkTracker(bot))
