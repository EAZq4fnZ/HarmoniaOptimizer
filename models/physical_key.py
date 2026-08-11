# models/physical_key.py

from dataclasses import dataclass

from models.position import Position


@dataclass(slots=True, frozen=True)
class PhysicalKey:
    id: str
    position: Position