from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast

import wavelink
from discord.ext import commands

from namek.cogs import BaseGroupCog, CogEnums
from namek.core.views.music_views import PlayLayoutView
from namek.utils import MainEmbed
from namek.utils.helper import make_song_media

if TYPE_CHECKING:
    from wavelink import TrackEndEventPayload, TrackStartEventPayload

    from namek.core import Bot
    from namek.utils.extras import NamekPlayer


_logger = logging.getLogger(__name__)


class WavelinkTracker(
    BaseGroupCog,
    name=CogEnums.WAVELINK_TRACKER_COG,
    group_description="Tracks the songs being played.",
):
    """Worker cog for handling new songs and queue ends in the VC."""

    def __init__(self, bot: Bot) -> None:
        super().__init__(logger=_logger)

    @commands.Cog.listener()
    async def on_wavelink_track_start(
        self,
        payload: TrackStartEventPayload,
    ) -> None:
        if payload.player is None:
            return

        player = cast("NamekPlayer", payload.player)

        artist = (
            f"[{payload.track.author}]({payload.track.artist.url})"
            if payload.track.artist.url
            else f"**{payload.track.author}**"
        )
        title = (
            f"[{payload.track.title}]({payload.track.uri})"
            if payload.track.uri
            else f"**{payload.track.title}**"
        )

        hours, rem = divmod(payload.track.length // 1000, 3600)
        minutes, seconds = divmod(rem, 60)
        if hours:
            duration_text = f"**{hours}**h **{minutes}**m **{seconds}**s"
        elif minutes:
            duration_text = f"**{minutes}**m **{seconds}**s"
        else:
            duration_text = f"**{seconds}**s"

        if player.song_message:
            await player.song_message.delete()

        song_media = await make_song_media(
            payload.track.title,
            payload.track.author,
            payload.player.client.loop,
        )
        view = PlayLayoutView(
            player=player,
            song_title=title,
            song_author=artist,
            duration=duration_text,
            media_file=song_media,
            thumbnail_url=payload.track.artwork,
        )
        message = await player.home_channel.send(
            view=view,
            file=song_media,
            silent=True,
        )
        player.song_message = message
        player.song_view = view

    @commands.Cog.listener()
    async def on_wavelink_track_end(
        self,
        payload: TrackEndEventPayload,
    ) -> None:
        if payload.player is None:
            return

        player = cast("NamekPlayer", payload.player)

        if not player.queue and not player.auto_queue:
            post_text = (
                "You can continue adding more tracks queue or "
                "listen to our fine tuned auto recommendation."
            )
            if player.autoplay is wavelink.AutoPlayMode.disabled:
                post_text = (
                    "You can continue listening to more songs by adding tracks to the queue."
                    " Since my autoplay is disabled I will leave the voice channel in a few "
                    "minutes if no songs are being played."
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
                description=post_text,
            )
            post_end_embed = (
                MainEmbed()
                .add_field(
                    name="Last played track",
                    value=f"** **\n{track}\n\n\\- {artist}",
                )
                .set_thumbnail(url=payload.track.artwork)
            )

            await player.home_channel.send(
                embeds=[track_end_embed, post_end_embed],
            )


async def setup(bot: Bot) -> None:
    await bot.add_cog(WavelinkTracker(bot))
