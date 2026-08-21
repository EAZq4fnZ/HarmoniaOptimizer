# optimizer/local_search_optimizer.py

from __future__ import annotations

from evaluator.candidate_evaluator import CandidateEvaluator
from evaluator.character_statistics import CharacterStatistics
from evaluator.transition_statistics import TransitionStatistics
from models.layout import Layout
from models.optimization_result import OptimizationResult
from models.optimization_step import OptimizationStep
from optimizer.best_candidate_selector import BestCandidateSelector
from optimizer.swap_candidate_generator import SwapCandidateGenerator


class LocalSearchOptimizer:
    """
    Optimize a layout using deterministic one-swap hill climbing.

    At each iteration:

    1. Generate every one-swap candidate.
    2. Evaluate every candidate.
    3. Select the valid candidate with the lowest score.
    4. Accept it only if it improves the current score.
    5. Record every accepted improvement.
    6. Repeat until no improvement exists or max_iterations is reached.
    """

    def __init__(
        self,
        candidate_evaluator: CandidateEvaluator,
        candidate_generator: SwapCandidateGenerator | None = None,
        candidate_selector: BestCandidateSelector | None = None,
        max_iterations: int = 100,
    ) -> None:
        if max_iterations < 0:
            raise ValueError(
                "max_iterations must be greater than or equal to 0"
            )

        self._candidate_evaluator = candidate_evaluator
        self._candidate_generator = (
            candidate_generator
            or SwapCandidateGenerator()
        )
        self._candidate_selector = (
            candidate_selector
            or BestCandidateSelector()
        )
        self._max_iterations = max_iterations

    @property
    def max_iterations(self) -> int:
        return self._max_iterations

    def optimize(
        self,
        layout: Layout,
        transition_statistics: TransitionStatistics,
        character_statistics: CharacterStatistics,
    ) -> OptimizationResult:
        """
        Return the complete result of the optimization run.
        """

        initial = self._candidate_evaluator.evaluate(
            layout=layout,
            transition_statistics=transition_statistics,
            character_statistics=character_statistics,
        )

        current = initial
        steps: list[OptimizationStep] = []

        if not current.is_valid:
            return OptimizationResult(
                initial_evaluation=initial,
                final_evaluation=current,
                steps=(),
            )

        if current.score is None:
            return OptimizationResult(
                initial_evaluation=initial,
                final_evaluation=current,
                steps=(),
            )

        for iteration in range(1, self._max_iterations + 1):
            candidate_layouts = (
                self._candidate_generator.generate(
                    current.layout
                )
            )

            evaluations = (
                self._candidate_evaluator.evaluate(
                    layout=candidate_layout,
                    transition_statistics=transition_statistics,
                    character_statistics=character_statistics,
                )
                for candidate_layout in candidate_layouts
            )

            best = self._candidate_selector.select(
                evaluations
            )

            if best is None:
                break

            if best.score is None:
                break

            if best.score >= current.score:
                break

            current = best

            steps.append(
                OptimizationStep(
                    iteration=iteration,
                    evaluation=current,
                )
            )

        return OptimizationResult(
            initial_evaluation=initial,
            final_evaluation=current,
            steps=tuple(steps),
        )