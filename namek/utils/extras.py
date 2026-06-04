from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import Message, TextChannel

    from namek.core.views.music_views import PlayLayoutView

__all__ = ("VCState",)


@dataclass(slots=True, kw_only=True)
class VCState:
    channel: TextChannel
    view: PlayLayoutView
    message: None | Message = None
