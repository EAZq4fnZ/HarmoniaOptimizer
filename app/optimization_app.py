# app/optimization_app.py

from __future__ import annotations

from config.harmonia_position_costs import (
    make_harmonia_position_cost_profile,
)
from evaluator.candidate_evaluator import CandidateEvaluator
from evaluator.candidate_scorer import CandidateScorer
from evaluator.character_analyzer import CharacterAnalyzer
from evaluator.constraint_factory import ConstraintFactory
from evaluator.corpus_analyzer import CorpusAnalyzer
from evaluator.finger_load_pipeline import FingerLoadPipeline
from evaluator.key_position_evaluator import KeyPositionEvaluator
from evaluator.layout_evaluator import LayoutEvaluator
from evaluator.trigram_layout_evaluator import TrigramLayoutEvaluator
from models.constraint_config import ConstraintConfig
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry
from models.layout import Layout
from models.multi_start_optimization_result import (
    MultiStartOptimizationResult,
)
from models.optimization_config import OptimizationConfig
from models.optimization_result import OptimizationResult
from models.search_budget import SearchBudget
from models.search_budget_profiles import SearchBudgetProfiles
from models.search_mode import SearchMode
from optimizer.local_search_optimizer import LocalSearchOptimizer
from optimizer.multi_start_optimizer import MultiStartOptimizer
from optimizer.random_start_layout_factory import (
    RandomStartLayoutFactory,
)
from optimizer.vowel_constrained_start_layout_factory import (
    VowelConstrainedStartLayoutFactory,
)
from reporting.optimization_reporter import OptimizationReporter


class OptimizationApp:
    """
    Application service for running one layout optimization.

    This class connects:

        Layout
        Corpus
          -> transition statistics
          -> character statistics
        ConstraintConfig
          -> ConstraintFactory
          -> ConstraintSet
        CandidateEvaluator
        LocalSearchOptimizer
        OptimizationReporter
    """

    def __init__(
        self,
        config: OptimizationConfig,
        constraint_config: ConstraintConfig,
        max_iterations: int = 10,
    ) -> None:
        if max_iterations < 0:
            raise ValueError(
                "max_iterations must be greater than or equal to 0"
            )

        self._config = config
        self._constraint_config = constraint_config
        self._max_iterations = max_iterations

    @property
    def config(self) -> OptimizationConfig:
        return self._config

    @property
    def constraint_config(self) -> ConstraintConfig:
        return self._constraint_config

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

        corpus_analyzer = CorpusAnalyzer()

        transition_statistics = corpus_analyzer.analyze(
            corpus
        )

        trigram_statistics = corpus_analyzer.analyze_trigrams(
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
            trigram_statistics=trigram_statistics,
        )

    def optimize_multi_start(
        self,
        layout: Layout,
        corpus: Corpus,
        runs: int,
        seed: int,
    ) -> MultiStartOptimizationResult:
        """
        Optimize from multiple reproducible
        random starting layouts.
        """

        corpus_analyzer = CorpusAnalyzer()

        transition_statistics = (
            corpus_analyzer.analyze(
                corpus
            )
        )

        trigram_statistics = (
            corpus_analyzer.analyze_trigrams(
                corpus
            )
        )

        character_statistics = (
            CharacterAnalyzer().analyze(
                corpus
            )
        )

        evaluator = (
            self._make_candidate_evaluator()
        )

        local_optimizer = (
            LocalSearchOptimizer(
                candidate_evaluator=evaluator,
                max_iterations=(
                    self._max_iterations
                ),
            )
        )

        use_vowel_constrained_factory = (
            self
            ._constraint_config
            .vowel_position
            .enabled
            or self
            ._constraint_config
            .vowel_hand_distribution
            .enabled
        )

        if use_vowel_constrained_factory:
            start_layout_factory = (
                VowelConstrainedStartLayoutFactory(
                    config=self._constraint_config,
                    seed=seed,
                )
            )
        else:
            start_layout_factory = (
                RandomStartLayoutFactory(
                    seed=seed
                )
            )

        optimizer = MultiStartOptimizer(
            local_optimizer=local_optimizer,
            start_layout_factory=(
                start_layout_factory
            ),
            runs=runs,
        )

        return optimizer.optimize(
            layout=layout,
            transition_statistics=(
                transition_statistics
            ),
            character_statistics=(
                character_statistics
            ),
            trigram_statistics=(
                trigram_statistics
            ),
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

    def optimize_with_budget(
        self,
        layout: Layout,
        corpus: Corpus,
        budget: SearchBudget,
        seed: int,
    ) -> MultiStartOptimizationResult:
        budget_app = OptimizationApp(
            config=self._config,
            constraint_config=(
                self._constraint_config
            ),
            max_iterations=(
                budget.max_iterations
            ),
        )

        return budget_app.optimize_multi_start(
            layout=layout,
            corpus=corpus,
            runs=budget.runs,
            seed=seed,
        )

    def optimize_with_mode(
        self,
        layout: Layout,
        corpus: Corpus,
        mode: SearchMode,
        profiles: SearchBudgetProfiles,
        seed: int,
    ) -> MultiStartOptimizationResult:
        budget = profiles.for_mode(
            mode
        )

        return self.optimize_with_budget(
            layout=layout,
            corpus=corpus,
            budget=budget,
            seed=seed,
        )

    def _make_candidate_evaluator(
        self,
    ) -> CandidateEvaluator:
        """
        Build the evaluator from supplied optimization
        and constraint configuration.
        """

        return CandidateEvaluator(
            constraint_set=ConstraintFactory.create(
                self._constraint_config
            ),
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
            trigram_layout_evaluator=TrigramLayoutEvaluator(
                self._config.trigram_cost_weights
            ),
            key_position_evaluator=KeyPositionEvaluator(
                make_harmonia_position_cost_profile()
            ),
        )