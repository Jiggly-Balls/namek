from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from disckit.utils.ui import BaseView
from discord import ButtonStyle
from discord.ui import Button

if TYPE_CHECKING:
    from discord import Interaction

    from namek.core import Bot


__all__ = ("PlayView",)


class PlayView(BaseView):
    def __init__(self) -> None:
        self.add_item(Button(style=ButtonStyle.grey))
        super().__init__(timeout=None)

    @discord.ui.button(emoji="⬅️", style=ButtonStyle.blurple)
    async def previous_callback(
        self, interaction: Interaction[Bot], button: Button["PlayView"]
    ) -> None: ...

    @discord.ui.button(emoji="🗑️", style=ButtonStyle.red)
    async def delete_callback(
        self, interaction: Interaction[Bot], button: Button["PlayView"]
    ) -> None: ...

    @discord.ui.button(emoji="➡️", style=ButtonStyle.blurple)
    async def next_callback(
        self, interaction: Interaction[Bot], button: Button["PlayView"]
    ) -> None: ...

    @discord.ui.button(label="\u200b", style=ButtonStyle.grey, disabled=True)
    async def dud_button(
        self, interaction: Interaction[Bot], button: Button["PlayView"]
    ) -> None: ...
