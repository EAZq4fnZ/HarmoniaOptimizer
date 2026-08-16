# models/transition.py
from dataclasses import dataclass

from .logical_key import LogicalKey


@dataclass(slots=True, frozen=True)
class Transition:
    source: LogicalKey
    target: LogicalKey