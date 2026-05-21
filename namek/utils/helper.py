from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from discord import Interaction, InteractionCallbackResponse

    from namek.core import Bot


__all__ = ("safe_defer",)


async def safe_defer(interaction: Interaction[Bot]) -> None | InteractionCallbackResponse[Bot]:
    if not interaction.response.is_done():
        return await interaction.response.defer()
