from __future__ import annotations

from typing import TYPE_CHECKING, cast

import discord

from namek.core.settings import EMOJIS
from namek.core.views.base_views import BaseLayoutView
from namek.utils.helper import safe_defer

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Self

    from discord import Interaction, Member, User
    from discord.ui import ActionRow, Button, Container

    from namek.core import Bot


__all__ = (
    "BasePaginator",
    "BasePaginatorPage",
)


class BasePaginatorPage(BaseLayoutView):
    """
    A custom base class containing the content for a particular paginator page.

    Parameters
    ----------
    parent_paginator : BasePaginator
        | The parent paginator instance of the page.
    author : int | User | Member
        | The user / member to which this pagination belongs to.
    timeout : None | float
        | In how many seconds the view will timeout.
    disable_on_timeout
        | If set to `True` it will disable all items in the view when it times out.
    stop_on_timeout
        | Stops the view from listening to any further events on timeout.

    """

    container: Container[Self] = discord.ui.Container()
    action_row: ActionRow[Self] = discord.ui.ActionRow()

    def __init__(
        self,
        parent_paginator: BasePaginator,
        author: int | User | Member | None = None,
        timeout: None | float = 180.0,
        disable_on_timeout: bool = True,
        stop_on_timeout: bool = True,
    ) -> None:
        super().__init__(
            author,
            timeout,
            disable_on_timeout,
            stop_on_timeout,
        )

        self.parent_paginator: BasePaginator = parent_paginator

    @action_row.button(emoji=EMOJIS.FIRST)
    async def first(self, interaction: Interaction[Bot], button: Button[Self]) -> None:
        paginator = self.parent_paginator
        paginator.index = 0

        await interaction.response.edit_message(view=paginator.pages[paginator.index])

    @action_row.button(emoji=EMOJIS.PREVIOUS)
    async def previous(
        self, interaction: Interaction[Bot], button: Button[Self]
    ) -> None:
        paginator = self.parent_paginator
        paginator.index = (paginator.index - 1) % len(paginator.pages)

        await interaction.response.edit_message(view=paginator.pages[paginator.index])

    @action_row.button(emoji=EMOJIS.DELETE)
    async def delete(self, interaction: Interaction[Bot], button: Button[Self]) -> None:
        interaction_message = cast("discord.Message", interaction.message)

        await interaction.response.defer()
        await interaction.followup.delete_message(interaction_message.id)

    @action_row.button(emoji=EMOJIS.NEXT)
    async def next(self, interaction: Interaction[Bot], button: Button[Self]) -> None:
        paginator = self.parent_paginator
        paginator.index = (paginator.index + 1) % len(paginator.pages)

        await interaction.response.edit_message(view=paginator.pages[paginator.index])

    @action_row.button(emoji=EMOJIS.LAST)
    async def last(self, interaction: Interaction[Bot], button: Button[Self]) -> None:
        paginator = self.parent_paginator
        paginator.index = len(self.parent_paginator.pages) - 1

        await interaction.response.edit_message(view=paginator.pages[paginator.index])


class BasePaginator:
    """
    A custom base paginator for handling multiple pages of content.

    Parameters
    ----------
    interaction : Interaction[Bot]
        | The interaction object.
    pages : Sequence[BasePaginatorPage]
        | A sequence of ``BasePaginatorPage`` instances to display from.
    author : int | User | Member
        | The user / member to which this pagination belongs to.
    timeout : None | float
        | In how many seconds the view will timeout.
    disable_on_timeout
        | If set to `True` it will disable all items in the view when it times out.
    stop_on_timeout
        | Stops the view from listening to any further events on timeout.

    """

    def __init__(
        self,
        interaction: Interaction[Bot],
        pages: Sequence[BasePaginatorPage],
        author: int | User | Member | None = None,
        timeout: None | float = 180.0,
        disable_on_timeout: bool = True,
        stop_on_timeout: bool = True,
    ) -> None:
        self.interaction: Interaction[Bot] = interaction
        self.pages: Sequence[BaseLayoutView] = pages
        self.index: int = 0

    async def start(self) -> None:
        await safe_defer(self.interaction)
        await self.interaction.followup.send(view=self.pages[self.index])
