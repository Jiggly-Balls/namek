from __future__ import annotations

from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = (
    "Settings",
    "BASE_DIR",
    "COG_DIRECTORIES",
)


class _Settings(BaseSettings, env_file=".env"):
    model_config: SettingsConfigDict = SettingsConfigDict(env_file=".env")

    BOT_TOKEN: SecretStr


Settings = _Settings()

BASE_DIR = Path(__file__).parent.parent
COG_DIRECTORIES = [
    BASE_DIR / "namek" / "cogs" / "commands",
    BASE_DIR / "namek" / "cogs" / "workers",
]
