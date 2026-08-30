# models/trigram_layout_evaluation.py

from __future__ import annotations

from dataclasses import dataclass

from .trigram_cost import TrigramCost
from .trigram_features import TrigramFeatures


@dataclass(slots=True, frozen=True)
class TrigramLayoutRecord:
    """
    Structural and cost contribution of one trigram.
    """

    first: str
    second: str
    third: str

    raw_count: int
    weighted_count: float

    features: TrigramFeatures
    cost: TrigramCost
    weighted_cost: float


@dataclass(slots=True, frozen=True)
class TrigramLayoutEvaluation:
    """
    Evaluation result for all supported trigrams in a layout.

    Lower total_cost and lower score are better.
    """

    total_cost: float

    evaluated_weight: float
    skipped_weight: float

    trigrams: tuple[TrigramLayoutRecord, ...]

    @property
    def trigram_count(self) -> int:
        return len(self.trigrams)

    @property
    def score(self) -> float:
        if self.evaluated_weight == 0.0:
            return 0.0

        return self.total_cost / self.evaluated_weight
