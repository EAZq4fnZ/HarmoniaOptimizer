# app/optimization_app.py

from __future__ import annotations

from evaluator.candidate_evaluator import CandidateEvaluator
from evaluator.candidate_scorer import CandidateScorer
from evaluator.character_analyzer import CharacterAnalyzer
from evaluator.constraint_set import ConstraintSet
from evaluator.corpus_analyzer import CorpusAnalyzer
from evaluator.finger_load_pipeline import FingerLoadPipeline
from evaluator.layout_evaluator import LayoutEvaluator
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry
from models.layout import Layout
from models.optimization_config import OptimizationConfig
from models.optimization_result import OptimizationResult
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
        config: OptimizationConfig,
        max_iterations: int = 10,
    ) -> None:
        if max_iterations < 0:
            raise ValueError(
                "max_iterations must be greater than or equal to 0"
            )

        self._config = config
        self._max_iterations = max_iterations

    @property
    def config(self) -> OptimizationConfig:
        return self._config

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

    def _make_candidate_evaluator(
        self,
    ) -> CandidateEvaluator:
        """
        Build the evaluator from the supplied optimization config.
        """

        return CandidateEvaluator(
            constraint_set=ConstraintSet(()),
            layout_evaluator=LayoutEvaluator(
                self._config.transition_cost_weights
            ),
            finger_load_pipeline=FingerLoadPipeline(),
            candidate_scorer=CandidateScorer(
                self._config.candidate_score_weights
            ),
            finger_load_budgets=(
                self._config.finger_load_budgets
            ),
        )