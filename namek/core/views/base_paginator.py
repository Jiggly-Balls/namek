from __future__ import annotations

from typing import TYPE_CHECKING

import discord

from namek.core.settings import EMOJIS
from namek.core.views import BaseLayoutView
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
