# evaluator/candidate_evaluator.py

# evaluator/candidate_evaluator.py

from __future__ import annotations

from evaluator.candidate_scorer import CandidateScorer
from evaluator.constraint_set import ConstraintSet
from evaluator.layout_evaluator import LayoutEvaluator
from evaluator.transition_statistics import TransitionStatistics
from models.candidate_evaluation import CandidateEvaluation
from models.layout import Layout


class CandidateEvaluator:
    """
    Evaluate one candidate keyboard layout.

    Hard constraints are evaluated first.

    Invalid candidates are rejected before the more expensive
    layout-cost evaluation is performed.
    """

    def __init__(
        self,
        constraint_set: ConstraintSet,
        layout_evaluator: LayoutEvaluator,
        candidate_scorer: CandidateScorer,
    ) -> None:
        self._constraint_set = constraint_set
        self._layout_evaluator = layout_evaluator
        self._candidate_scorer = candidate_scorer

    def evaluate(
        self,
        layout: Layout,
        statistics: TransitionStatistics,
    ) -> CandidateEvaluation:
        """
        Evaluate one candidate layout.
        """

        constraint_evaluation = self._constraint_set.evaluate(
            layout
        )

        if not constraint_evaluation.is_valid:
            return CandidateEvaluation(
                layout=layout,
                constraint_evaluation=constraint_evaluation,
                layout_evaluation=None,
                candidate_score=None,
            )

        layout_evaluation = self._layout_evaluator.evaluate(
            layout,
            statistics,
        )

        candidate_score = self._candidate_scorer.score(
            layout_evaluation=layout_evaluation,
            finger_load_evaluations=(),
        )

        return CandidateEvaluation(
            layout=layout,
            constraint_evaluation=constraint_evaluation,
            layout_evaluation=layout_evaluation,
            candidate_score=candidate_score,
        )