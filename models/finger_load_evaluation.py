# models/finger_load_evaluation.py

from __future__ import annotations

from dataclasses import dataclass

from models.enums import Finger, Hand


@dataclass(slots=True, frozen=True)
class FingerLoadEvaluation:
    """
    Evaluation result for one hand/finger pair.
    """

    hand: Hand
    finger: Finger

    actual_ratio: float
    target_ratio: float
    tolerance: float

    excess_ratio: float
    penalty: float