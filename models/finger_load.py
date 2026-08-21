# models/finger_load.py

from __future__ import annotations

from dataclasses import dataclass

from models.enums import Finger, Hand


@dataclass(slots=True, frozen=True)
class FingerLoad:
    """
    Character load assigned to one hand/finger pair.

    raw_count
        Number of characters assigned to the finger.

    weighted_count
        Character count after corpus-entry weights are applied.
    """

    hand: Hand
    finger: Finger
    raw_count: int
    weighted_count: float