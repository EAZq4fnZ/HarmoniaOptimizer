from dataclasses import dataclass

from .position import Position


@dataclass(slots=True, frozen=True)
class Key:
    label: str
    position: Position
    category: str = "alpha"