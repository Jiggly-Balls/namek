from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING

from discord.utils import MISSING
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    from pathlib import Path
    from typing import ClassVar

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
    OWNER_IDS: list[int] = MISSING

    LAVALINK_NAME: str = MISSING
    LAVALINK_URI: SecretStr = MISSING
    LAVALINK_PASSWORD: SecretStr = MISSING
    LAVALINK_TRACK_CACHE: int = MISSING
    LAVALINK_RETRIES: int = MISSING


SETTINGS: _Settings = _Settings()

BASE_DIR: Path = pathlib.Path(__file__).parent.parent
COG_DIRECTORIES: list[Path] = [
    BASE_DIR / "cogs" / "commands",
    BASE_DIR / "cogs" / "workers",
]
