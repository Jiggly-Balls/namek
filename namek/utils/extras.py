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

    class NamekPlayer(wavelink.Player):
        home_channel: TextChannel = MISSING
        song_message: Message = MISSING
        song_view: PlayLayoutView = MISSING

        def __init__(
            self,
            client: Client = MISSING,
            channel: Connectable = MISSING,
            *,
            nodes: list[Node] | None = None,
            **kwargs: Any,
        ) -> None:
            super().__init__(client=client, channel=channel, nodes=nodes)


__all__ = ("namek_player_factory",)


def namek_player_factory(
    *,
    home_channel: TextChannel = MISSING,
    song_message: Message = MISSING,
    song_view: PlayLayoutView = MISSING,
) -> type[NamekPlayer]:
    return type(
        "NamekPlayer",
        (wavelink.Player,),
        {
            "home_channel": home_channel,
            "song_message": song_message,
            "song_view": song_view,
        },
    )  # pyright: ignore[reportReturnType]
