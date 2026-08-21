# models/finger_load_budget.py

from __future__ import annotations

from dataclasses import dataclass

from models.enums import Finger, Hand


@dataclass(slots=True, frozen=True)
class FingerLoadBudget:
    """
    Target load ratio for one hand/finger pair.

    target_ratio
        Desired share of the total weighted character load.

    tolerance
        Amount by which the actual ratio may exceed the target
        before a penalty is applied.
    """

    hand: Hand
    finger: Finger
    target_ratio: float
    tolerance: float = 0.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.target_ratio <= 1.0:
            raise ValueError(
                "target_ratio must be between 0.0 and 1.0"
            )

        if not 0.0 <= self.tolerance <= 1.0:
            raise ValueError(
                "tolerance must be between 0.0 and 1.0"
            )