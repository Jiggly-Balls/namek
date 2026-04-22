from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from disckit.utils import MentionTree
from discord.ext import commands

if TYPE_CHECKING:
    from collections.abc import Collection

    from discord import Intents


_logger: logging.Logger = logging.getLogger(__name__)


class Bot(commands.Bot):
    def __init__(
        self, *, intents: Intents, owner_ids: None | Collection[int] = None
    ) -> None:
        """
        Initialize the bot instance.

        Parameters
        ----------
        intents : discord.Intents
            The intents to be used by the bot for interacting with Discord.
        """
        super().__init__(
            command_prefix="/",
            intents=intents,
            help_command=None,
            tree_cls=MentionTree,
            owner_ids=owner_ids,
            chunk_guilds_at_startup=False,
        )
        self.tree: MentionTree
