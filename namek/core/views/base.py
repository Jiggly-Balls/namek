from __future__ import annotations

import logging
import sys
import traceback
from typing import TYPE_CHECKING

import discord
from disckit.utils import ErrorEmbed
from discord.ui import View

from namek.core.settings import SETTINGS
from namek.utils import ErrorEmbed

if TYPE_CHECKING:
    from typing import Any

    from discord import Interaction, InteractionMessage, Member, Message, User
    from discord.ui import Item

    from namek.core.bot import Bot


__all__ = ("BaseView",)


logger = logging.getLogger(__name__)


class BaseView(View):
    """A custom base view which extends `discord.ui.View`
    to provide more inbuilt features.

    Parameters
    ----------
    author
        | The author of the `View`. If set to `None` anyone can interact with the `View`.
    timeout
        | In how many seconds the view will timeout.
    disable_on_timeout
        | If set to `True` it will disable all items in the view when it times out.
    stop_on_timeout
        | Stops the view from listening to any further events on timeout.
    """

    def __init__(
        self,
        author: None | int | User | Member = None,
        timeout: None | float = 180.0,
        disable_on_timeout: bool = True,
        stop_on_timeout: bool = True,
    ) -> None:
        super().__init__(timeout=timeout)

        self.message: None | Message | InteractionMessage = None

        self._author: None | int | User | Member = author
        if isinstance(self._author, (discord.User, discord.Member)):
            self._author = self._author.id
        self._disable_on_timeout: bool = disable_on_timeout
        self._stop_on_timeout: bool = stop_on_timeout

    def disable_all_items(self) -> None:
        """Disables all items in the View when called."""

        for item in self.children:
            item.disabled = True  # pyright:ignore[reportAttributeAccessIssue]

    async def on_timeout(self) -> None:
        if self._disable_on_timeout:
            self.disable_all_items()
            if self.message:
                try:
                    await self.message.edit(view=self)
                except discord.errors.NotFound:
                    pass
                except discord.errors.HTTPException as e:
                    if e.code == 50027:
                        logger.error(
                            "Invalid Webhook Token: Unable to edit the message."
                        )
                    elif e.code == 10008:
                        logger.error(
                            "Unknown Message: The message was deleted."
                        )
                    else:
                        raise e
            else:
                raise Warning(
                    f"{traceback.format_exc()}\n\n"
                    f"BaseView.message was not defined in view: {self} to disable the items.",
                )

        if self._stop_on_timeout:
            self.stop()

    async def interaction_check(self, interaction: Interaction[Bot]) -> bool:  # pyright: ignore[reportIncompatibleMethodOverride]
        if self._author is None or interaction.user.id == self._author:
            return True

        await interaction.response.send_message(
            embed=ErrorEmbed(description="This interaction is not for you!"),
            ephemeral=True,
        )
        return False

    async def on_error(
        self, interaction: Interaction, error: Exception, item: Item[Any]
    ) -> None:
        if not SETTINGS.BUG_REPORT_CHANNEL_ID:
            return await super().on_error(interaction, error, item)

        send_message_func = (
            interaction.followup.send
            if interaction.response.is_done()
            else interaction.response.send_message
        )
        await send_message_func(
            embed=ErrorEmbed(
                title="Sorry :(",
                description="An unexpected error has occurred. The developers have been notified of this.",
            )
        )

        print(
            f"Ignoring exception in view {item.view or self} for item {item}:",
            file=sys.stderr,
        )
        traceback.print_exception(
            type(error), error, error.__traceback__, file=sys.stderr
        )

        channel = interaction.client.get_channel(
            SETTINGS.BUG_REPORT_CHANNEL_ID
        ) or await interaction.client.fetch_channel(
            SETTINGS.BUG_REPORT_CHANNEL_ID
        )

        frame = (
            error.__traceback__.tb_frame if error.__traceback__ else "Unkown"
        )

        embed = ErrorEmbed()
        embed.add_field(name="Error in View", value=f"{item.view or self}")
        embed.add_field(
            name="Error in Item", value=f"Author Name: {interaction.user}"
        )
        embed.add_field(name="Error Type", value=f"{type(error)}")
        embed.add_field(name="Error Type Description", value=str(frame))
        embed.add_field(
            name="Cause", value=f"{error.with_traceback(error.__traceback__)}"
        )

        await channel.send(  # pyright:ignore[reportAttributeAccessIssue, reportUnknownMemberType]
            embed=embed
        )
