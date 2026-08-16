# models/logical_key.py
from dataclasses import dataclass

from .logical_position import LogicalPosition


@dataclass(slots=True, frozen=True)
class LogicalKey:
    """A key assigned to a logical position."""

    id: str
    position: LogicalPosition