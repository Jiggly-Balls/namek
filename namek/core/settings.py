from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING

import discord
from discord.utils import MISSING
from PIL import ImageFont
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    from pathlib import Path
    from typing import ClassVar

    from discord import Colour, Emoji
    from PIL.ImageFont import FreeTypeFont

__all__ = (
    "SETTINGS",
    "BASE_DIR",
    "COG_DIRECTORIES",
)


class _Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env"
    )

    BOT_TOKEN: SecretStr = MISSING

    DEV_GUILD_ID: int = MISSING
    BUG_REPORT_CHANNEL_ID: int = MISSING
    OWNER_IDS: list[int] = MISSING

    LAVALINK_NAME: str = MISSING
    LAVALINK_URI: SecretStr = MISSING
    LAVALINK_PASSWORD: SecretStr = MISSING
    LAVALINK_TRACK_CACHE: int = MISSING
    LAVALINK_RETRIES: int = MISSING


SETTINGS: _Settings = _Settings()


class _Emojis:
    AUTOPLAY_DISABLED: Emoji = MISSING
    AUTOPLAY_ENABLED: Emoji = MISSING
    DISCONNECT: Emoji = MISSING
    FILTER: Emoji = MISSING
    NEXT: Emoji = MISSING
    PLAY: Emoji = MISSING
    PAUSE: Emoji = MISSING
    PREVIOUS: Emoji = MISSING
    REPEAT_1: Emoji = MISSING
    REPEAT: Emoji = MISSING
    SHUFFLE: Emoji = MISSING


EMOJIS: _Emojis = _Emojis()

BASE_DIR: Path = pathlib.Path(__file__).parent.parent
ASSET_DIR: Path = BASE_DIR / "assets"
GRAPHICS_DIR: Path = ASSET_DIR / "graphics"
FONTS_DIR: Path = ASSET_DIR / "fonts"

EMOJIS_DIR: Path = GRAPHICS_DIR / "emojis"
OTHER_DIR: Path = GRAPHICS_DIR / "other"

COG_DIRECTORIES: list[Path] = [
    BASE_DIR / "cogs" / "commands",
    BASE_DIR / "cogs" / "workers",
]

DEFAULT_FONT: str = "BebasNeue-Regular.ttf"
TITLE_FONT_SIZE: int = 32
AUTHOR_FONT_SIZE: int = 24
TITLE_FONT: FreeTypeFont = ImageFont.truetype(
    FONTS_DIR / DEFAULT_FONT, TITLE_FONT_SIZE
)
AUTHOR_FONT: FreeTypeFont = ImageFont.truetype(
    FONTS_DIR / DEFAULT_FONT, AUTHOR_FONT_SIZE
)

DEFAULT_GRADIENT: str = "gradient.png"
IMAGE_SIZE: tuple[int, int] = (500, 150)
BACKGROUND_COLOUR: tuple[int, int, int] = (43, 43, 43)
ANTI_ALIAS_TOLERANCE: int = 40

STATUS_COOLDOWN: float = 600.0
ALLOWED_MUSIC_SOURCES: set[str] = {
    "www.youtube.com",
    "www.music.youtube.com",
    "youtube.com",
    "music.youtube.com",
    "soundcloud.com",
    "www.soundcloud.com",
    "music.apple.com",
    "www.music.apple.com",
    "youtu.be",
    "www.youtu.be",
}

MAIN_COLOUR: Colour = discord.Colour.blue()
ERROR_COLOUR: Colour = discord.Colour.red()
SUCCESS_COLOUR: Colour = discord.Colour.green()
