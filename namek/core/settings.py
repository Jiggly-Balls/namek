from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING

import discord
from discord.utils import MISSING
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    from pathlib import Path
    from typing import ClassVar

    from discord import Emoji

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
COG_DIRECTORIES: list[Path] = [
    BASE_DIR / "cogs" / "commands",
    BASE_DIR / "cogs" / "workers",
]

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

MAIN_COLOUR = discord.Colour.blue()
ERROR_COLOUR = discord.Colour.red()
SUCCESS_COLOUR = discord.Colour.green()
