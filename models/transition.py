# models/transition.py
from dataclasses import dataclass

from .logical_key import LogicalKey


@dataclass(slots=True, frozen=True)
class Transition:
    """
    A transition between two logical keys.

    Represents one key-to-key movement.

    Example
    -------
    H -> E
    """

    source: LogicalKey
    target: LogicalKey