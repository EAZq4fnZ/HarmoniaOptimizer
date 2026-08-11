# models/keyboard.py

from dataclasses import dataclass

from .geometry import Geometry
from .logical_key import LogicalKey
from .physical_key import PhysicalKey


@dataclass(slots=True)
class Keyboard:
    name: str

    physical: dict[str, PhysicalKey]
    logical: dict[str, LogicalKey]
    geometry: Geometry