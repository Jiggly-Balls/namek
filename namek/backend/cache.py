from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import ClassVar
 
    from wavelink import Player

    from namek.utils.extras import VCState


__all__ = ("Cache",)


class Cache:
    """
    The bot's shared external cache.

    These attributes can be accessed globally but should be used sparingly,
    as there is no explicit way to track their usage across the codebase.
    This cache is only used when it is not feasible to pass data locally.

    Attributes
    ----------
    vc_states : dict of int to tuple of (BaseView, Message)
        A dictionary mapping guild IDs to their respective voice channel states.
    """

    vc_states: ClassVar[dict[Player, VCState]] = {}
