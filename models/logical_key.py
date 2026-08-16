# models/logical_key.py
from dataclasses import dataclass

from .logical_position import LogicalPosition


@dataclass(slots=True, frozen=True)
class LogicalKey:
    id: str
    position: LogicalPosition