from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Embed

from namek.core.settings import ERROR_COLOUR, MAIN_COLOUR, SUCCESS_COLOUR

if TYPE_CHECKING:
    from typing import Any

    from discord import Embed


__all__ = ("ErrorEmbed", "MainEmbed", "SuccessEmbed")


class MainEmbed(Embed):
    def __init__(
        self,
        *,
        title: None | str = None,
        description: None | str = None,
        url: None | str = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            colour=MAIN_COLOUR,
            title=title,
            url=url,
            description=description,
            **kwargs,
        )


class ErrorEmbed(Embed):
    def __init__(
        self,
        *,
        title: None | str = None,
        description: None | str = None,
        url: None | str = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            colour=ERROR_COLOUR,
            title=title,
            url=url,
            description=description,
            **kwargs,
        )


class SuccessEmbed(Embed):
    def __init__(
        self,
        *,
        title: None | str = None,
        description: None | str = None,
        url: None | str = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            colour=SUCCESS_COLOUR,
            title=title,
            url=url,
            description=description,
            **kwargs,
        )
