# models/transition.py
from dataclasses import dataclass

from .logical_key import LogicalKey


@dataclass(slots=True, frozen=True)
class Transition:
    source: LogicalKey
    target: LogicalKey

    @property
    def source_position(self):
        return self.source.position

    @property
    def target_position(self):
        return self.target.position