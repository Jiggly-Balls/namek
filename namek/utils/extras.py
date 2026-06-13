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
    """
    Dataclass to represent every instance of music playing across all VCs.
    This is used in the bot's singleton cache.

    Parameters
    ----------
    channel : TextChannel
        The channel where the song info message has been sent to.
    message : Message
        The message object of the song info.
    view : PlayLayoutView
        The view object attached to the message.

    """

    channel: TextChannel
    message: Message = MISSING
    view: PlayLayoutView = MISSING
