# models/logical_key.py
from dataclasses import dataclass

from .logical_position import LogicalPosition


@dataclass(slots=True, frozen=True)
class LogicalKey:
    """
    A logical keyboard key.

    A LogicalKey represents a character/key and the logical
    position assigned to it.

    Example
    -------
    A -> LogicalPosition(...)
    """

    id: str
    position: LogicalPosition