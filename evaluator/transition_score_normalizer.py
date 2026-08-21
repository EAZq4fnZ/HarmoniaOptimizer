# evaluator/transition_score_normalizer.py

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NormalizedTransitionScore:
    """
    Normalized transition score.

    Lower is better.
    """

    total_cost: float
    evaluated_weight: float

    def __post_init__(self) -> None:
        if self.evaluated_weight < 0:
            raise ValueError(
                "evaluated_weight must be non-negative"
            )

    @property
    def score(self) -> float:
        if self.evaluated_weight == 0:
            return 0.0

        return self.total_cost / self.evaluated_weight


def normalize_transition_score(
    total_cost: float,
    evaluated_weight: float,
) -> NormalizedTransitionScore:
    """
    Normalize total transition cost by evaluated transition weight.
    """

    return NormalizedTransitionScore(
        total_cost=total_cost,
        evaluated_weight=evaluated_weight,
    )