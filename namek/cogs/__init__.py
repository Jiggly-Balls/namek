from __future__ import annotations

from enum import StrEnum, auto
from typing import TYPE_CHECKING

from discord.ext.commands import GroupCog

if TYPE_CHECKING:
    from logging import Logger


__all__ = ("BaseGroupCog", "CogEnums")


class BaseGroupCog(GroupCog):
    """The base group cog which comes along with basic logging."""

    def __init__(self, logger: None | Logger = None) -> None:
        super().__init__()
        self.logger: None | Logger = logger

    async def cog_load(self) -> None:
        if self.logger:
            self.logger.info(f"Cog: {self.qualified_name} has been loaded.")

    async def cog_unload(self) -> None:
        if self.logger:
            self.logger.info(f"Cog: {self.qualified_name} has been unloaded.")


class CogEnums(StrEnum):
    """Enums for representing cog names."""

    DEV_COG = auto()
    MUSIC_COG = auto()
    ERROR_HANDLER_COG = auto()
    STATUS_HANDLER_COG = auto()
    WAVELINK_HEALTH_COG = auto()
    WAVELINK_TRACKER_COG = auto()
