# app/optimization_app.py

from __future__ import annotations

from evaluator.candidate_evaluator import CandidateEvaluator
from evaluator.candidate_scorer import CandidateScorer
from evaluator.character_analyzer import CharacterAnalyzer
from evaluator.constraint_set import ConstraintSet
from evaluator.corpus_analyzer import CorpusAnalyzer
from evaluator.finger_load_pipeline import FingerLoadPipeline
from evaluator.layout_evaluator import LayoutEvaluator
from models.candidate_score import CandidateScoreWeights
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry
from models.enums import Finger, Hand
from models.finger_load_budget import FingerLoadBudget
from models.layout import Layout
from models.optimization_result import OptimizationResult
from models.transition_cost import TransitionCostWeights
from optimizer.local_search_optimizer import LocalSearchOptimizer
from reporting.optimization_reporter import OptimizationReporter


class OptimizationApp:
    """
    Application service for running one layout optimization.

    This class connects:

        Layout
        Corpus
          -> transition statistics
          -> character statistics
        CandidateEvaluator
        LocalSearchOptimizer
        OptimizationReporter
    """

    def __init__(
        self,
        max_iterations: int = 10,
    ) -> None:
        if max_iterations < 0:
            raise ValueError(
                "max_iterations must be greater than or equal to 0"
            )

        self._max_iterations = max_iterations

    @property
    def max_iterations(self) -> int:
        return self._max_iterations

    def optimize(
        self,
        layout: Layout,
        corpus: Corpus,
    ) -> OptimizationResult:
        """
        Optimize one layout against one corpus.
        """

        transition_statistics = CorpusAnalyzer().analyze(
            corpus
        )

        character_statistics = CharacterAnalyzer().analyze(
            corpus
        )

        evaluator = self._make_candidate_evaluator()

        optimizer = LocalSearchOptimizer(
            candidate_evaluator=evaluator,
            max_iterations=self._max_iterations,
        )

        return optimizer.optimize(
            layout=layout,
            transition_statistics=transition_statistics,
            character_statistics=character_statistics,
        )

    def optimize_text(
        self,
        layout: Layout,
        text: str,
    ) -> OptimizationResult:
        """
        Optimize a layout against one text string.
        """

        corpus = Corpus(
            entries=(
                CorpusEntry(
                    text=text,
                ),
            ),
        )

        return self.optimize(
            layout=layout,
            corpus=corpus,
        )

    def format_result(
        self,
        result: OptimizationResult,
    ) -> str:
        """
        Format an optimization result for display.
        """

        return OptimizationReporter().format(
            result
        )

    @staticmethod
    def _make_candidate_evaluator() -> CandidateEvaluator:
        """
        Build the default evaluator used by the application.

        These weights are initial defaults. They will later move
        into configuration rather than remaining hard-coded here.
        """

        transition_weights = TransitionCostWeights(
            same_finger_penalty=10.0,
            same_hand_penalty=2.0,
            row_change_penalty=1.5,
            alternation_reward=2.0,
            inward_roll_reward=1.5,
            outward_roll_reward=0.5,
        )

        candidate_weights = CandidateScoreWeights(
            transition_weight=1.0,
            finger_load_weight=1.0,
        )

        finger_load_budgets = (
            FingerLoadBudget(
                hand=Hand.LEFT,
                finger=Finger.INDEX,
                target_ratio=0.25,
                tolerance=0.05,
            ),
            FingerLoadBudget(
                hand=Hand.LEFT,
                finger=Finger.MIDDLE,
                target_ratio=0.15,
                tolerance=0.05,
            ),
            FingerLoadBudget(
                hand=Hand.LEFT,
                finger=Finger.RING,
                target_ratio=0.07,
                tolerance=0.03,
            ),
            FingerLoadBudget(
                hand=Hand.LEFT,
                finger=Finger.PINKY,
                target_ratio=0.03,
                tolerance=0.02,
            ),
            FingerLoadBudget(
                hand=Hand.RIGHT,
                finger=Finger.INDEX,
                target_ratio=0.25,
                tolerance=0.05,
            ),
            FingerLoadBudget(
                hand=Hand.RIGHT,
                finger=Finger.MIDDLE,
                target_ratio=0.15,
                tolerance=0.05,
            ),
            FingerLoadBudget(
                hand=Hand.RIGHT,
                finger=Finger.RING,
                target_ratio=0.07,
                tolerance=0.03,
            ),
            FingerLoadBudget(
                hand=Hand.RIGHT,
                finger=Finger.PINKY,
                target_ratio=0.03,
                tolerance=0.02,
            ),
        )

        return CandidateEvaluator(
            constraint_set=ConstraintSet(()),
            layout_evaluator=LayoutEvaluator(
                transition_weights
            ),
            finger_load_pipeline=FingerLoadPipeline(),
            candidate_scorer=CandidateScorer(
                candidate_weights
            ),
            finger_load_budgets=finger_load_budgets,
        )