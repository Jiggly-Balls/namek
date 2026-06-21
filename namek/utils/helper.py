from __future__ import annotations

import io
import string
from typing import TYPE_CHECKING, cast

import discord
import googletrans
from PIL import Image, ImageDraw

from namek.core.settings import (
    ANTI_ALIAS_TOLERANCE,
    AUTHOR_FONT,
    BACKGROUND_COLOUR,
    DEFAULT_GRADIENT,
    IMAGE_SIZE,
    OTHER_DIR,
    TITLE_FONT,
)
from namek.utils import ErrorEmbed

if TYPE_CHECKING:
    from asyncio import AbstractEventLoop

    from discord import (
        File,
        Interaction,
        InteractionCallbackResponse,
    )
    from discord.voice_client import VocalGuildChannel

    from namek.core import Bot


__all__ = ("make_song_media", "safe_defer", "vc_check")
_ALLOWED_CHARS: str = (
    string.ascii_letters + string.punctuation + string.whitespace + "0123456789"
)


async def safe_defer(
    interaction: Interaction[Bot],
    /,
) -> None | InteractionCallbackResponse[Bot]:
    if not interaction.response.is_done():
        return await interaction.response.defer()


async def vc_check(interaction: Interaction[Bot]) -> None | VocalGuildChannel:
    interaction_user = cast("discord.Member", interaction.user)

    send_message_func = (
        interaction.followup.send
        if interaction.response.is_done()
        else interaction.response.send_message
    )

    if not (interaction_user.voice and interaction_user.voice.channel):
        await send_message_func(
            embed=ErrorEmbed(
                description="You need to be within a voice channel to use this command.",
            ),
            ephemeral=True,
        )
        return None

    return interaction_user.voice.channel


def _cleanup_text(text: str) -> str:
    new_text = ""
    for char in text:
        if 31 < ord(char) < 127:
            new_text += char
    return new_text


def _pil_media_handle(title: str, author: str) -> File:
    background = Image.open(OTHER_DIR / DEFAULT_GRADIENT).convert("RGBA")
    background = background.resize(IMAGE_SIZE)  # pyright: ignore[reportUnknownMemberType]
    image = Image.new("RGBA", size=IMAGE_SIZE, color=BACKGROUND_COLOUR)

    colour_target: tuple[int, int, int] = (0, 0, 0)  # Black

    draw = ImageDraw.Draw(image)
    draw.text(
        (15, 15),
        title,
        font=TITLE_FONT,
        fill=colour_target,
    )
    draw.text(
        (15, 75),
        text=f"— {author}",
        font=AUTHOR_FONT,
        fill=colour_target,
    )

    new_image_data: list[tuple[int, int, int, int]] = []
    pixel_data = image.get_flattened_data()
    if TYPE_CHECKING:
        pixel_data = cast("tuple[tuple[int, ...], ...]", pixel_data)

    for r, g, b, a in pixel_data:
        if r == g == b == 0:
            new_image_data.append((r, g, b, 0))

        elif (
            abs(r - colour_target[0]) <= ANTI_ALIAS_TOLERANCE
            and abs(g - colour_target[1]) <= ANTI_ALIAS_TOLERANCE
            and abs(b - colour_target[2]) <= ANTI_ALIAS_TOLERANCE
        ):
            new_image_data.append(
                (r, g, b, int(0.30 * r) + int(0.59 * g) + int(0.11 * b)),
            )
        else:
            new_image_data.append((r, g, b, a))

    image.putdata(new_image_data)  # pyright: ignore[reportUnknownMemberType]
    background.paste(image, mask=image)

    x, y = 300, 0
    block_width, block_height = IMAGE_SIZE[0] - x, IMAGE_SIZE[1]
    fade_out_colour = (*BACKGROUND_COLOUR, 255)

    overlay = Image.new("RGBA", (block_width, block_height), fade_out_colour)

    for px in range(block_width):
        a = int(255 * px / (block_width - 1))
        for py in range(block_height):
            overlay.putpixel((px, py), (43, 43, 43, a))

    background.paste(overlay, (x, y), overlay)

    with io.BytesIO() as image_binary:
        background.save(image_binary, "PNG")
        image_binary.seek(0)
        file = discord.File(fp=image_binary, filename="image.png")

    return file


async def make_song_media(
    song_title: str,
    song_author: str,
    event_loop: AbstractEventLoop,
) -> File:
    async with googletrans.Translator() as translator:
        if not all(char in _ALLOWED_CHARS for char in song_title):
            title_result = await translator.translate(song_title)
            title_result_str = title_result.pronunciation or title_result.text
        else:
            title_result_str = song_title

        if not all(char in _ALLOWED_CHARS for char in song_author):
            author_result = await translator.translate(song_author)
            author_result_str = author_result.pronunciation or author_result.text
        else:
            author_result_str = song_author

    normalized_title = title_result_str or _cleanup_text(song_title)
    normalized_author = author_result_str or _cleanup_text(song_author)

    media_file = await event_loop.run_in_executor(
        None,
        _pil_media_handle,
        normalized_title,
        normalized_author,
    )

    return media_file
