from __future__ import annotations

from typing import TYPE_CHECKING, cast

import discord

from namek.core.settings import EMOJIS
from namek.core.views import BaseView
from namek.utils.helper import safe_defer

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any

    from discord import Embed, Interaction, Member, User
    from discord.ui import Button

    from namek.core import Bot
    from namek.core.views import BaseLayoutView


__all__ = ("BasePaginator",)


class BasePaginator(BaseView):
    def __init__(
        self,
        interaction: Interaction[Bot],
        pages: Sequence[BaseLayoutView | Embed],
        author: int | User | Member | None = None,
        timeout: None | float = 180.0,
        disable_on_timeout: bool = True,
        stop_on_timeout: bool = True,
    ) -> None:
        super().__init__(
            author=author,
            timeout=timeout,
            disable_on_timeout=disable_on_timeout,
            stop_on_timeout=stop_on_timeout,
        )

        self.interaction: Interaction[Bot] = interaction
        self.pages: Sequence[BaseLayoutView | Embed] = pages
        self.index: int = 0

    def _build_kwargs(self) -> dict[str, Any]:
        kwargs: dict[str, Any] = {}

        page = self.pages[self.index]
        if isinstance(page, discord.Embed):
            kwargs["embed"] = page
        else:
            kwargs["view"] = page

        return kwargs

    async def start(self) -> None:
        await safe_defer(self.interaction)

        await self.interaction.followup.send(**self._build_kwargs())

    @discord.ui.button(emoji=EMOJIS.FIRST)
    async def first(
        self, interaction: Interaction[Bot], button: Button[BasePaginator]
    ) -> None:
        self.index = 0

        interaction_message = cast("discord.Message", self.interaction.message)
        await self.interaction.followup.edit_message(
            interaction_message.id, **self._build_kwargs()
        )

    @discord.ui.button(emoji=EMOJIS.PREVIOUS)
    async def previous(
        self, interaction: Interaction[Bot], button: Button[BasePaginator]
    ) -> None:
        self.index -= 1
        if self.index < 0:
            self.index = len(self.pages)

        interaction_message = cast("discord.Message", self.interaction.message)
        await self.interaction.followup.edit_message(
            interaction_message.id, **self._build_kwargs()
        )

    @discord.ui.button(emoji=EMOJIS.NEXT)
    async def next(
        self, interaction: Interaction[Bot], button: Button[BasePaginator]
    ) -> None:
        self.index += 1
        if self.index > len(self.pages):
            self.index = 0

        interaction_message = cast("discord.Message", self.interaction.message)
        await self.interaction.followup.edit_message(
            interaction_message.id, **self._build_kwargs()
        )

    @discord.ui.button(emoji=EMOJIS.LAST)
    async def last(
        self, interaction: Interaction[Bot], button: Button[BasePaginator]
    ) -> None:
        self.index = len(self.pages)

        interaction_message = cast("discord.Message", self.interaction.message)
        await self.interaction.followup.edit_message(
            interaction_message.id, **self._build_kwargs()
        )
