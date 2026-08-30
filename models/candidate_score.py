# models/candidate_score.py

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CandidateScoreWeights:
    """
    Weights used to combine normalized candidate scores.
    """

    transition_weight: float = 1.0
    trigram_weight: float = 0.0
    finger_load_weight: float = 1.0

    def __post_init__(self) -> None:
        if self.transition_weight < 0:
            raise ValueError(
                "transition_weight must be non-negative"
            )

        if self.trigram_weight < 0:
            raise ValueError(
                "trigram_weight must be non-negative"
            )

        if self.finger_load_weight < 0:
            raise ValueError(
                "finger_load_weight must be non-negative"
            )


@dataclass(frozen=True, slots=True)
class CandidateScore:
    """
    Combined score for one valid candidate layout.

    Lower is better.
    """

    transition_score: float
    finger_load_score: float
    weights: CandidateScoreWeights
    trigram_score: float = 0.0

    @property
    def weighted_transition_score(self) -> float:
        return (
            self.transition_score
            * self.weights.transition_weight
        )

    @property
    def weighted_trigram_score(self) -> float:
        return (
            self.trigram_score
            * self.weights.trigram_weight
        )

    @property
    def weighted_finger_load_score(self) -> float:
        return (
            self.finger_load_score
            * self.weights.finger_load_weight
        )

    @property
    def total(self) -> float:
        return (
            self.weighted_transition_score
            + self.weighted_trigram_score
            + self.weighted_finger_load_score
        )
