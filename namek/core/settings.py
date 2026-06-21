import pathlib
from pathlib import Path
from typing import ClassVar

import discord
from discord import Colour, Emoji
from discord.utils import MISSING
from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = (
    "ALLOWED_NETLOC_SOURCES",
    "ALLOWED_SOURCE_NAMES",
    "ALLOWED_STREAMING_SOURCES",
    "ANTI_ALIAS_TOLERANCE",
    "ASSET_DIR",
    "AUTHOR_FONT",
    "AUTHOR_FONT_SIZE",
    "BACKGROUND_COLOUR",
    "BASE_DIR",
    "COG_DIRECTORIES",
    "DEFAULT_FONT",
    "DEFAULT_GRADIENT",
    "EMOJIS",
    "EMOJIS_DIR",
    "ERROR_COLOUR",
    "FONTS_DIR",
    "GRAPHICS_DIR",
    "IMAGE_SIZE",
    "MAIN_COLOUR",
    "OTHER_DIR",
    "SETTINGS",
    "STATUS_COOLDOWN",
    "SUCCESS_COLOUR",
    "TITLE_FONT",
    "TITLE_FONT_SIZE",
)


class _Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
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
    def __init__(self) -> None:
        self.AUTOPLAY_DISABLED: Emoji = MISSING
        self.AUTOPLAY_ENABLED: Emoji = MISSING
        self.DISCONNECT: Emoji = MISSING
        self.FILTER: Emoji = MISSING
        self.FIRST: Emoji = MISSING
        self.LAST: Emoji = MISSING
        self.NEXT: Emoji = MISSING
        self.PLAY: Emoji = MISSING
        self.PAUSE: Emoji = MISSING
        self.PREVIOUS: Emoji = MISSING
        self.REPEAT_1: Emoji = MISSING
        self.REPEAT: Emoji = MISSING
        self.SHUFFLE: Emoji = MISSING


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
    FONTS_DIR / DEFAULT_FONT,
    TITLE_FONT_SIZE,
)
AUTHOR_FONT: FreeTypeFont = ImageFont.truetype(
    FONTS_DIR / DEFAULT_FONT,
    AUTHOR_FONT_SIZE,
)

DEFAULT_GRADIENT: str = "gradient.png"
IMAGE_SIZE: tuple[int, int] = (500, 150)
BACKGROUND_COLOUR: tuple[int, int, int] = (43, 43, 43)
ANTI_ALIAS_TOLERANCE: int = 40

STATUS_COOLDOWN: float = 600.0

ALLOWED_STREAMING_SOURCES: dict[str, tuple[str, ...]] = {
    "Youtube / Youtube Music": (
        "music.youtube.com",
        "www.music.youtube.com",
        "www.youtube.com",
        "youtu.be",
        "youtube.com",
    ),
    "Sound Cloud": (
        "soundcloud.com",
        "www.soundcloud.com",
    ),
    "Bandcamp": (
        "bandcamp.com",
        "www.bandcamp.com",
    ),
    "Vimeo": (
        "vimeo.com",
        "www.vimeo.com",
    ),
}
ALLOWED_NETLOC_SOURCES: set[str] = {
    netloc for source in ALLOWED_STREAMING_SOURCES.values() for netloc in source
}
ALLOWED_SOURCE_NAMES: tuple[str, ...] = tuple(ALLOWED_STREAMING_SOURCES)

MAIN_COLOUR: Colour = discord.Colour.blue()
ERROR_COLOUR: Colour = discord.Colour.red()
SUCCESS_COLOUR: Colour = discord.Colour.green()
