# models/position.py
from dataclasses import dataclass

"""
from .enums import Finger, Hand, Layer, Row

@dataclass(slots=True, frozen=True)
class Position:
    layer: Layer
    hand: Hand
    finger: Finger
    row: Row
    column: int
    physical_column: int | None = None
"""

@dataclass(slots=True, frozen=True)
class Position:
    x: float
    y: float
    z: float