# evaluator/candidate_scorer.py

from __future__ import annotations

from evaluator.transition_score_normalizer import (
    normalize_transition_score,
)
from models.candidate_score import (
    CandidateScore,
    CandidateScoreWeights,
)
from models.finger_load_evaluation import FingerLoadEvaluation
from models.layout_evaluation import LayoutEvaluation
from models.trigram_layout_evaluation import (
    TrigramLayoutEvaluation,
)


class CandidateScorer:
    """
    Combine transition, trigram, and finger-load evaluations
    into one candidate score.

    Lower is better.
    """

    def __init__(
        self,
        weights: CandidateScoreWeights,
    ) -> None:
        self._weights = weights

    @property
    def weights(self) -> CandidateScoreWeights:
        return self._weights

    def score(
        self,
        layout_evaluation: LayoutEvaluation,
        finger_load_evaluations: tuple[
            FingerLoadEvaluation,
            ...
        ],
        trigram_layout_evaluation: (
            TrigramLayoutEvaluation | None
        ) = None,
    ) -> CandidateScore:
        """
        Build the combined score for one valid candidate.

        Transition score:
            total transition cost / evaluated transition weight

        Trigram score:
            total trigram cost / evaluated trigram weight

            Zero when no trigram evaluation is supplied.

        Finger-load score:
            sum of all finger-load penalties
        """

        normalized_transition = normalize_transition_score(
            total_cost=layout_evaluation.total_cost,
            evaluated_weight=layout_evaluation.evaluated_weight,
        )

        if trigram_layout_evaluation is None:
            trigram_score = 0.0
        else:
            trigram_score = (
                trigram_layout_evaluation.score
            )

        finger_load_score = sum(
            evaluation.penalty
            for evaluation in finger_load_evaluations
        )

        return CandidateScore(
            transition_score=normalized_transition.score,
            finger_load_score=finger_load_score,
            weights=self._weights,
            trigram_score=trigram_score,
        )
