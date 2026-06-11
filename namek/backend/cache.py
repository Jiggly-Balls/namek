from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wavelink import Player

    from namek.utils.extras import VCState


__all__ = ("CACHE",)


class _Cache:
    """A singleton for the bot's shared external cache.

    Attributes
    ----------
    vc_states : dict[Player, VCState]
        | A dictionary mapping the player to it's VC state composing of the channel and
        | message objects.
    """

    vc_states: dict[Player, VCState] = {}

    def delete_vc_state(self, player: Player) -> None:
        try:
            del self.vc_states[player]
        except KeyError:
            pass


CACHE: _Cache = _Cache()
