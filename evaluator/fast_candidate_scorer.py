# evaluator/fast_candidate_scorer.py

from __future__ import annotations

from models.candidate_score import CandidateScoreWeights


class FastCandidateScorer:
    """
    Combine precomputed transition, trigram, and finger-load scores
    without building detailed evaluation objects.

    Lower is better.
    """

    def __init__(
        self,
        weights: CandidateScoreWeights,
    ) -> None:
        self._weights = weights

    @property
    def weights(
        self,
    ) -> CandidateScoreWeights:
        return self._weights

    def score(
        self,
        *,
        transition_total_cost: float,
        evaluated_transition_weight: float,
        finger_load_penalty: float,
        trigram_total_cost: float = 0.0,
        evaluated_trigram_weight: float = 0.0,
    ) -> float:
        """
        Return the same final numeric score as CandidateScorer.

        Transition score:
            transition_total_cost / evaluated_transition_weight

        Trigram score:
            trigram_total_cost / evaluated_trigram_weight

        Finger-load score:
            sum of finger-load penalties

        Zero evaluated weight produces a zero normalized score for
        the corresponding component.
        """

        if evaluated_transition_weight < 0.0:
            raise ValueError(
                "evaluated_transition_weight "
                "must be non-negative"
            )

        if evaluated_trigram_weight < 0.0:
            raise ValueError(
                "evaluated_trigram_weight "
                "must be non-negative"
            )

        if evaluated_transition_weight == 0.0:
            transition_score = 0.0
        else:
            transition_score = (
                transition_total_cost
                / evaluated_transition_weight
            )

        if evaluated_trigram_weight == 0.0:
            trigram_score = 0.0
        else:
            trigram_score = (
                trigram_total_cost
                / evaluated_trigram_weight
            )

        return (
            transition_score
            * self._weights.transition_weight
            + trigram_score
            * self._weights.trigram_weight
            + finger_load_penalty
            * self._weights.finger_load_weight
        )
