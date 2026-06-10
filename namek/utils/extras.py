from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from discord.utils import MISSING

if TYPE_CHECKING:
    from discord import Message, TextChannel

    from namek.core.views.music_views import PlayLayoutView

__all__ = ("VCState",)


@dataclass(slots=True, kw_only=True)
class VCState:
    channel: TextChannel
    message: None | Message = None
    view: PlayLayoutView = MISSING
