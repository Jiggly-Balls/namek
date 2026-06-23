from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Embed

from namek.core.settings import ERROR_COLOUR, MAIN_COLOUR, SUCCESS_COLOUR

if TYPE_CHECKING:
    import datetime
    from typing import NotRequired, TypedDict, Unpack

    from discord.types.embed import EmbedType

    class EmbedKwargs(TypedDict):
        type: NotRequired[EmbedType]
        timestamp: NotRequired[None | datetime.datetime]


__all__ = (
    "ErrorEmbed",
    "MainEmbed",
    "SuccessEmbed",
)


class MainEmbed(Embed):
    """The main embed for when no errors / success specific operations occur."""

    def __init__(
        self,
        *,
        title: None | str = None,
        description: None | str = None,
        url: None | str = None,
        **kwargs: Unpack[EmbedKwargs],
    ) -> None:
        super().__init__(
            colour=MAIN_COLOUR,
            title=title,
            url=url,
            description=description,
            **kwargs,
        )


class ErrorEmbed(Embed):
    """An embed to represent error / unexpected output."""

    def __init__(
        self,
        *,
        title: None | str = None,
        description: None | str = None,
        url: None | str = None,
        **kwargs: Unpack[EmbedKwargs],
    ) -> None:
        super().__init__(
            colour=ERROR_COLOUR,
            title=title,
            url=url,
            description=description,
            **kwargs,
        )


class SuccessEmbed(Embed):
    """An embed to represent success."""

    def __init__(
        self,
        *,
        title: None | str = None,
        description: None | str = None,
        url: None | str = None,
        **kwargs: Unpack[EmbedKwargs],
    ) -> None:
        super().__init__(
            colour=SUCCESS_COLOUR,
            title=title,
            url=url,
            description=description,
            **kwargs,
        )
