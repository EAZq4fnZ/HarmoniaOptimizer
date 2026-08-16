# models/logical_position.py
from dataclasses import dataclass

from .enums import Finger, Hand, Layer, Row


@dataclass(slots=True, frozen=True)
class LogicalPosition:
    """Logical position of a key in the keyboard layout."""

    layer: Layer
    hand: Hand
    finger: Finger
    row: Row
    column: int