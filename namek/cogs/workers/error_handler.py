from __future__ import annotations

import logging
import sys
import traceback
from typing import TYPE_CHECKING

import discord
from discord import Interaction, app_commands
from discord.ext import commands

from namek.cogs import BaseGroupCog, CogEnums
from namek.core.settings import SETTINGS
from namek.utils import ErrorEmbed

if TYPE_CHECKING:
    from collections.abc import Callable
    from types import CoroutineType
    from typing import Any

    from discord import Client, DiscordException, Embed
    from discord.app_commands import AppCommandError, Group
    from discord.app_commands.tree import CommandTree

    from namek.core import Bot

_logger = logging.getLogger(__name__)
type DefaultErrorHandler = Callable[
    [CommandTree[Client], Interaction[Client], AppCommandError],
    CoroutineType[Any, Any, None],
]

# https://discord.com/developers/docs/topics/opcodes-and-status-codes#json-json-error-codes
UNKNOWN_INTERACTION: set[int] = {10062, 10015}


class ErrorHandler(
    BaseGroupCog,
    name=CogEnums.ERROR_HANDLER_COG,
    group_description="Catches and cleanly logs and handles any unhandled errors.",
):
    """Worker cog for redirecting & handling all errors raised during it's lifetime."""

    def __init__(self, bot: Bot) -> None:
        super().__init__(_logger)

        self.bot: Bot = bot
        self.default_error_handler: DefaultErrorHandler = (
            app_commands.CommandTree.on_error
        )

    async def cog_load(self) -> None:
        app_commands.CommandTree.on_error = self.on_error  # pyright:ignore[reportAttributeAccessIssue]
        await super().cog_load()

    async def cog_unload(self) -> None:
        app_commands.CommandTree.on_error = self.default_error_handler
        await super().cog_unload()

    @staticmethod
    def _get_group_names(
        group: Group,
        all_groups: None | list[str] = None,
    ) -> list[str]:
        all_groups = all_groups or []
        all_groups.append(group.name)
        if group.parent is None:
            return all_groups
        return ErrorHandler._get_group_names(group.parent, all_groups)

    @staticmethod
    async def send_response(
        *,
        interaction: Interaction,
        embed: None | Embed = None,
        content: None | str = None,
        ephemeral: bool = True,
    ) -> None:
        """Handles the error response to user."""
        load: dict[str, Any] = {"ephemeral": ephemeral}
        if embed:
            load["embed"] = embed
        if content:
            load["content"] = content

        try:
            if interaction.response.is_done():
                await interaction.followup.send(**load)
            else:
                await interaction.response.send_message(**load)
        except discord.InteractionResponded:
            await interaction.followup.send(**load)

    @staticmethod
    async def throw_err(
        interaction: Interaction,
        error: DiscordException,
    ) -> None:
        print(
            f"Ignoring exception in command {interaction.command}:",
            file=sys.stderr,
        )
        traceback.print_exception(
            type(error),
            error,
            error.__traceback__,
            file=sys.stderr,
        )

        if SETTINGS.BUG_REPORT_CHANNEL_ID is not None:
            channel = interaction.client.get_channel(
                SETTINGS.BUG_REPORT_CHANNEL_ID,
            ) or await interaction.client.fetch_channel(
                SETTINGS.BUG_REPORT_CHANNEL_ID,
            )

            frame = error.__traceback__.tb_frame if error.__traceback__ else "Unkown"
            command_name = "Command not found"
            if interaction.command:
                final_name = []
                if (
                    not isinstance(
                        interaction.command,
                        app_commands.ContextMenu,
                    )
                    and interaction.command.parent
                ):
                    final_name = ErrorHandler._get_group_names(
                        interaction.command.parent,
                    )
                final_name.append(interaction.command.name)
                command_name = "/" + (" ".join(final_name))

            log_embed = ErrorEmbed(title=f"Error in Commnd: {command_name}")
            log_embed.add_field(
                name="Caused by",
                value=f"Author Name: `{interaction.user}`",
                inline=False,
            )
            log_embed.add_field(
                name="Error Type",
                value=f"`{type(error)}`",
                inline=False,
            )
            log_embed.add_field(
                name="Error Frame",
                value=f"```\n{frame}\n```",
                inline=False,
            )
            log_embed.add_field(
                name="Error Traceback",
                value=f"```\n{error.with_traceback(error.__traceback__)}\n```",
                inline=False,
            )

            await channel.send(  # pyright:ignore[reportAttributeAccessIssue, reportUnknownMemberType]
                embed=log_embed,
            )
        else:
            _logger.warning(
                "SETTINGS.BUG_REPORT_CHANNEL_ID is MISSING. Could not report bug report through discord.",
            )

        response_embed = ErrorEmbed(
            title="Sorry...",
            description="An unexpected error has occurred.\nThe developers have been notified of it.",
        )
        await ErrorHandler.send_response(
            interaction=interaction,
            embed=response_embed,
        )

    async def on_error(
        self,
        interaction: Interaction,
        error: AppCommandError,
    ) -> None:
        error_embed = ErrorEmbed(title="Error")

        if isinstance(interaction.channel, discord.DMChannel):
            return

        if isinstance(error, discord.NotFound):
            if error.code in UNKNOWN_INTERACTION:
                return

        elif isinstance(error, commands.errors.NotOwner):
            error_embed.description = "This command is only available to owners!"
            await ErrorHandler.send_response(
                interaction=interaction,
                embed=error_embed,
            )

        elif isinstance(error, app_commands.BotMissingPermissions):
            missing_permissions = ", ".join(error.missing_permissions)
            error_embed.description = (
                f"I don't have the required permissions for this command. "
                f"I need `{missing_permissions}` permission(s) to proceed with this command."
            )
            await ErrorHandler.send_response(
                interaction=interaction,
                embed=error_embed,
                ephemeral=True,
            )

        elif isinstance(error, app_commands.MissingPermissions):
            missing_permissions = ", ".join(error.missing_permissions)
            error_embed.description = (
                f"You don't have the required permissions for this command, "
                f"you need ``{missing_permissions}`` permission to use this command."
            )
            await ErrorHandler.send_response(
                interaction=interaction,
                embed=error_embed,
                ephemeral=True,
            )

        elif isinstance(error, app_commands.CommandSignatureMismatch):
            error_embed.description = (
                f"The signature of the command `{error.command.name}` seems to be different"
                " by the one provided by discord. Please try using the command again later."
                " If this issue still persists, please contact the bot owners to resync the"
                " commands."
            )
            await ErrorHandler.send_response(
                interaction=interaction,
                embed=error_embed,
            )

        elif isinstance(error, app_commands.CommandNotFound):
            error_embed.description = (
                "There seems to be a mismatch in the registered command name and with the command present in the source."
                " Please contact the bot owners to resync the commands."
            )
        else:
            await ErrorHandler.throw_err(interaction=interaction, error=error)


async def setup(bot: Bot) -> None:
    await bot.add_cog(ErrorHandler(bot))
