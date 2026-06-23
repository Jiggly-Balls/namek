from __future__ import annotations

import itertools
from typing import TYPE_CHECKING, cast, final

import discord
from discord import ButtonStyle

from namek.core.settings import EMOJIS, MAIN_COLOUR
from namek.core.views import BaseLayoutView, BasePaginator, BasePaginatorPage
from namek.utils import ErrorEmbed, MainEmbed
from namek.utils.helper import vc_check

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any

    from discord import File, Interaction, InteractionMessage
    from discord.ui import ActionRow, Button, Container

    from namek.core import Bot
    from namek.utils.extras import NamekPlayer


__all__ = (
    "PlayLayoutView",
    "QueueListPaginator",
)


@final
class PlayLayoutView(BaseLayoutView):
    """
    A music view class for any new song about to be played.
    This view contains various information such as song title, author, thumbnail, etc.
    """

    container: Container[PlayLayoutView] = discord.ui.Container(
        accent_colour=MAIN_COLOUR
    )
    row1: ActionRow[PlayLayoutView] = discord.ui.ActionRow()
    row2: ActionRow[PlayLayoutView] = discord.ui.ActionRow()

    def __init__(
        self,
        player: NamekPlayer,
        song_title: str,
        song_author: str,
        media_file: None | File,
        thumbnail_url: None | str,
    ) -> None:
        super().__init__(timeout=None)

        self.player: NamekPlayer = player
        self.is_paused: bool = False

        _section_kwargs: dict[str, Any] = {}
        if thumbnail_url:
            _section_kwargs["accessory"] = discord.ui.Thumbnail["PlayLayoutView"](
                media=thumbnail_url
            )

        title_section = discord.ui.Section["PlayLayoutView"](
            discord.ui.TextDisplay(
                content=f"## {song_title}\n**  **—{song_author}",
            ),
            **_section_kwargs,
        )
        self.container.add_item(title_section)

        if media_file:
            media_section = discord.ui.MediaGallery["PlayLayoutView"](
                discord.MediaGalleryItem(media=media_file),
            )
            self.container.add_item(media_section)

    async def interaction_check(self, interaction: Interaction[Bot]) -> bool:
        channel = await vc_check(interaction)
        return channel is not None

    @row1.button(label="\u200b", style=ButtonStyle.grey, disabled=True)
    async def dud_button_1(
        self,
        interaction: Interaction[Bot],
        button: Button[PlayLayoutView],
    ) -> None: ...

    @row1.button(emoji=EMOJIS.PREVIOUS, style=ButtonStyle.blurple)
    async def previous_callback(
        self,
        interaction: Interaction[Bot],
        button: Button[PlayLayoutView],
    ) -> None:
        await interaction.response.defer(ephemeral=True)

        await vc_check(interaction)

        if self.player.queue.history and len(self.player.queue.history) > 1:
            current_track = self.player.current
            if current_track:
                self.player.queue.put_at(0, current_track)

            previous_track = self.player.queue.history.get_at(-2)
            await self.player.play(previous_track)

            embed = MainEmbed(
                title="Track Rewinded",
                description=f"Rewinded to: **{previous_track}**",
            )
        else:
            embed = ErrorEmbed(
                title="Error",
                description="No previous track found in the history.",
            )

        await interaction.followup.send(embed=embed, ephemeral=True)

    @row1.button(emoji=EMOJIS.DISCONNECT, style=ButtonStyle.red)
    async def delete_callback(
        self,
        interaction: Interaction[Bot],
        button: Button[PlayLayoutView],
    ) -> None:
        await interaction.response.defer()

        channel = await vc_check(interaction)
        if not channel or not interaction.message:
            return

        interaction_guild = cast("discord.Guild", interaction.guild)
        interaction_guild_voice_client = cast(
            "discord.VoiceProtocol", interaction_guild.voice_client
        )

        if not self.player.connected:
            await interaction.followup.send(
                embed=ErrorEmbed(
                    description="The player has already disconnected.",
                ),
                ephemeral=True,
            )
            return

        await self.player.song_message.delete()
        await self.player.pause(True)
        await interaction_guild_voice_client.disconnect(force=False)

        await interaction.followup.send(
            embed=MainEmbed(
                description=f"Disconnected from voice channel `{channel.name}`",
            ),
        )
        self.stop()

    @row1.button(emoji=EMOJIS.NEXT, style=ButtonStyle.blurple)
    async def next_callback(
        self,
        interaction: Interaction[Bot],
        button: Button[PlayLayoutView],
    ) -> None:
        await interaction.response.defer(ephemeral=True)

        await self.player.skip(force=True)
        current_song = self.player.current
        if not current_song:
            return

        await interaction.followup.send(
            embed=MainEmbed(
                description=f"Skipped current song. Now playing `{current_song.title}`",
            ),
            ephemeral=True,
        )

    @row1.button(label="\u200b", style=ButtonStyle.grey, disabled=True)
    async def dud_button_2(
        self,
        interaction: Interaction[Bot],
        button: Button[PlayLayoutView],
    ) -> None: ...

    @row2.button(label="\u200b", style=ButtonStyle.grey, disabled=True)
    async def dud_button_3(
        self,
        interaction: Interaction[Bot],
        button: Button[PlayLayoutView],
    ) -> None: ...

    @row2.button(label="\u200b", style=ButtonStyle.grey, disabled=True)
    async def dud_button_4(
        self,
        interaction: Interaction[Bot],
        button: Button[PlayLayoutView],
    ) -> None: ...

    @row2.button(emoji=EMOJIS.PAUSE, style=ButtonStyle.green)
    async def play_pause(
        self,
        interaction: Interaction[Bot],
        button: Button[PlayLayoutView],
    ) -> None:
        await interaction.response.defer(ephemeral=True)

        self.is_paused = not self.is_paused
        await self.player.pause(self.is_paused)

        if interaction.message:
            button.emoji = EMOJIS.PLAY if self.is_paused else EMOJIS.PAUSE
            await interaction.followup.edit_message(
                interaction.message.id,
                view=self,
            )
        if self.is_paused:
            message = "Paused the current track."
        else:
            message = "Resuming the current track."

        await interaction.followup.send(
            embed=MainEmbed(description=message),
            ephemeral=True,
        )

    @row2.button(label="\u200b", style=ButtonStyle.grey, disabled=True)
    async def dud_button_5(
        self,
        interaction: Interaction[Bot],
        button: Button[PlayLayoutView],
    ) -> None: ...

    @row2.button(label="\u200b", style=ButtonStyle.grey, disabled=True)
    async def dud_button_6(
        self,
        interaction: Interaction[Bot],
        button: Button[PlayLayoutView],
    ) -> None: ...


@final
class _QueueListPage(BasePaginatorPage):
    def __init__(
        self,
        songs: tuple[str, ...],
        paginator_reference: QueueListPaginator,
        original_response: InteractionMessage,
        author: int,
    ) -> None:
        super().__init__(paginator_reference, author=author)

        for song in songs:
            self.container.add_item(discord.ui.TextDisplay(song))
            self.container.add_item(
                discord.ui.Separator(spacing=discord.SeparatorSpacing.small)
            )

        self.message = original_response
        self.container.accent_colour = MAIN_COLOUR


@final
class QueueListPaginator(BasePaginator):
    def __init__(
        self,
        interaction: Interaction[Bot],
        original_response: InteractionMessage,
        author: int,
        songs: Sequence[str],
        items_per_page: int,
    ) -> None:
        self.author: int = author
        self.original_response = original_response
        pages = self._build_pages(songs, items_per_page)

        super().__init__(interaction=interaction, pages=pages, author=author)

    def _build_pages(
        self, songs: Sequence[str], items_per_page: int
    ) -> list[_QueueListPage]:
        song_list: list[_QueueListPage] = []

        for page in itertools.batched(songs, items_per_page):
            song_list.append(  # noqa: PERF401
                _QueueListPage(
                    songs=page,
                    paginator_reference=self,
                    original_response=self.original_response,
                    author=self.author,
                )
            )

        return song_list
