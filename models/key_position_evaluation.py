# models/key_position_evaluation.py

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class KeyPositionEvaluation:
    """
    Aggregate unigram key-position evaluation for one layout.

    Lower score is better.
    """

    total_cost: float
    evaluated_weight: float
    skipped_weight: float

    @property
    def score(self) -> float:
        if self.evaluated_weight <= 0.0:
            return 0.0

        return (
            self.total_cost
            / self.evaluated_weight
        )