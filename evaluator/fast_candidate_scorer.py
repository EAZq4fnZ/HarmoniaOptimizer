# evaluator/fast_candidate_scorer.py

from __future__ import annotations

from models.candidate_score import CandidateScoreWeights


class FastCandidateScorer:
    """
    Combine precomputed transition and finger-load scores
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
    ) -> float:
        """
        Return the same final numeric score as CandidateScorer.

        Transition score:
            total_cost / evaluated_weight

        Finger-load score:
            sum of finger-load penalties
        """

        if evaluated_transition_weight < 0.0:
            raise ValueError(
                "evaluated_transition_weight "
                "must be non-negative"
            )

        if evaluated_transition_weight == 0.0:
            transition_score = 0.0
        else:
            transition_score = (
                transition_total_cost
                / evaluated_transition_weight
            )

        return (
            transition_score
            * self._weights.transition_weight
            + finger_load_penalty
            * self._weights.finger_load_weight
        )