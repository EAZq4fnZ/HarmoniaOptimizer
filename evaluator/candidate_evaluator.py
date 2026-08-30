# evaluator/candidate_evaluator.py

from __future__ import annotations

from evaluator.candidate_scorer import CandidateScorer
from evaluator.character_statistics import CharacterStatistics
from evaluator.constraint_set import ConstraintSet
from evaluator.finger_load_pipeline import FingerLoadPipeline
from evaluator.layout_evaluator import LayoutEvaluator
from evaluator.transition_statistics import TransitionStatistics
from evaluator.trigram_layout_evaluator import (
    TrigramLayoutEvaluator,
)
from evaluator.trigram_statistics import TrigramStatistics
from models.candidate_evaluation import CandidateEvaluation
from models.finger_load_budget import FingerLoadBudget
from models.layout import Layout


class CandidateEvaluator:
    """
    Evaluate one candidate keyboard layout.

    Evaluation order
    ----------------
    1. Hard constraints
    2. Transition/layout evaluation
    3. Trigram evaluation
    4. Finger-load evaluation
    5. Combined candidate score

    Invalid candidates are rejected before the more expensive
    soft-evaluation stages are performed.
    """

    def __init__(
        self,
        constraint_set: ConstraintSet,
        layout_evaluator: LayoutEvaluator,
        finger_load_pipeline: FingerLoadPipeline,
        candidate_scorer: CandidateScorer,
        finger_load_budgets: tuple[FingerLoadBudget, ...],
        trigram_layout_evaluator: (
            TrigramLayoutEvaluator | None
        ) = None,
    ) -> None:
        self._constraint_set = constraint_set
        self._layout_evaluator = layout_evaluator
        self._finger_load_pipeline = finger_load_pipeline
        self._candidate_scorer = candidate_scorer
        self._finger_load_budgets = finger_load_budgets
        self._trigram_layout_evaluator = (
            trigram_layout_evaluator
        )

    def evaluate(
        self,
        layout: Layout,
        transition_statistics: TransitionStatistics,
        character_statistics: CharacterStatistics,
        trigram_statistics: TrigramStatistics | None = None,
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
            transition_statistics,
        )

        trigram_layout_evaluation = None

        if (
            self._trigram_layout_evaluator is not None
            and trigram_statistics is not None
        ):
            trigram_layout_evaluation = (
                self._trigram_layout_evaluator.evaluate(
                    layout,
                    trigram_statistics,
                )
            )

        finger_load_evaluations = (
            self._finger_load_pipeline.evaluate(
                layout=layout,
                statistics=character_statistics,
                budgets=self._finger_load_budgets,
            )
        )

        candidate_score = self._candidate_scorer.score(
            layout_evaluation=layout_evaluation,
            finger_load_evaluations=finger_load_evaluations,
            trigram_layout_evaluation=(
                trigram_layout_evaluation
            ),
        )

        return CandidateEvaluation(
            layout=layout,
            constraint_evaluation=constraint_evaluation,
            layout_evaluation=layout_evaluation,
            candidate_score=candidate_score,
        )
