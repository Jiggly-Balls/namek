from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import Interaction

    from namek.core import Bot


__all__ = ("safe_defer",)


async def safe_defer(interaction: Interaction[Bot]) -> None:
    if not interaction.response.is_done():
        await interaction.response.defer()
