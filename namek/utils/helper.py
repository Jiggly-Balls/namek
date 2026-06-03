from __future__ import annotations

from typing import TYPE_CHECKING

import discord
import googletrans

from namek.utils import ErrorEmbed

if TYPE_CHECKING:
    from asyncio import AbstractEventLoop

    from discord import File, Interaction, InteractionCallbackResponse
    from discord.voice_client import VocalGuildChannel

    from namek.core import Bot


__all__ = ("safe_defer", "vc_check")


async def safe_defer(
    interaction: Interaction[Bot],
) -> None | InteractionCallbackResponse[Bot]:
    if not interaction.response.is_done():
        return await interaction.response.defer()


async def vc_check(interaction: Interaction[Bot]) -> None | VocalGuildChannel:
    assert isinstance(interaction.user, discord.Member)

    if not (interaction.user.voice and interaction.user.voice.channel):
        send_message_func = (
            interaction.followup.send
            if interaction.response.is_done()
            else interaction.response.send_message
        )

        await send_message_func(
            embed=ErrorEmbed(
                description="You need to be within a voice channel to use this command."
            ),
            ephemeral=True,
        )
        return None
    return interaction.user.voice.channel


def _cleanup_text(text: str) -> str:
    new_text = ""
    for char in text:
        if 31 < ord(char) < 127:
            new_text += char
    return new_text


def _pil_media_handle(tite: str, author: str) -> File: ...


async def make_song_media(
    song_title: str,
    song_author: str,
    event_loop: AbstractEventLoop,
) -> File:
    async with googletrans.Translator() as translator:
        title_result = await translator.translate(song_title)
        author_result = await translator.translate(song_author)

    normalized_title = (
        title_result.pronunciation
        or title_result.text
        or _cleanup_text(song_title)
    )
    normalized_author = (
        author_result.pronunciation
        or author_result.text
        or _cleanup_text(song_author)
    )

    media_file = await event_loop.run_in_executor(
        None,
        _pil_media_handle,
        normalized_title,
        normalized_author,
    )

    return media_file