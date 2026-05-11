from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import Message
    from discord.interactions import InteractionChannel


@dataclass(slots=True, kw_only=True)
class VCState:
    channel: InteractionChannel
    message: None | Message = None