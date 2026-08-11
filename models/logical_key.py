# models/logical_key.py

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class LogicalKey:
    id: str
    hand: str
    finger: str
    row: str
    column: str