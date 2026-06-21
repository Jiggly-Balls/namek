from __future__ import annotations

from typing import TYPE_CHECKING

import wavelink
from discord.utils import MISSING

if TYPE_CHECKING:
    from typing import Any

    from discord import Client, Message, TextChannel
    from discord.abc import Connectable
    from wavelink import Node

    from namek.core.views.music_views import PlayLayoutView


__all__ = ("NamekPlayer",)


class NamekPlayer(wavelink.Player):
    """The custom wavelink player subclass."""

    def __init__(
        self,
        client: Client = MISSING,
        channel: Connectable = MISSING,
        *,
        nodes: list[Node] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(client=client, channel=channel, nodes=nodes)

        self.home_channel: TextChannel = MISSING
        self.song_message: Message = MISSING
        self.song_view: PlayLayoutView = MISSING
