from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast

import discord
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

        self.bot: Bot = bot

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
        duration_text = f"{hours:02}:{minutes:02}:{seconds:02}"

        if player.song_message:
            try:
                await player.song_message.delete()
            except discord.errors.NotFound:
                pass

        try:
            song_media = await make_song_media(
                song_title=payload.track.title,
                song_author=payload.track.author,
                song_duration=duration_text,
                event_loop=payload.player.client.loop,
            )
        except Exception:
            song_media = None
            _logger.exception(
                'Failed to create song media for song title: "%s" & author: "%s"',
                payload.track.title,
                payload.track.author,
                stack_info=True,
            )

        view = PlayLayoutView(
            player=player,
            song_title=title,
            song_author=artist,
            media_file=song_media,
            thumbnail_url=payload.track.artwork,
        )

        if song_media:
            message = await player.home_channel.send(
                view=view,
                file=song_media,
                silent=True,
            )
        else:
            message = await player.home_channel.send(
                view=view,
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
