from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import Message, TextChannel


__all__ = ("VCState",)


@dataclass(slots=True, kw_only=True)
class VCState:
    channel: TextChannel
    message: None | Message = None
