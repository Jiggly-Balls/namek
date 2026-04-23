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
    "Settings",
    "BASE_DIR",
    "COG_DIRECTORIES",
)


class _Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env"
    )

    BOT_TOKEN: SecretStr = MISSING


Settings = _Settings()

BASE_DIR: Path = pathlib.Path(__file__).parent.parent
COG_DIRECTORIES: list[Path] = [
    BASE_DIR / "cogs" / "commands",
    BASE_DIR / "cogs" / "workers",
]
