# optimizer/multi_start_optimizer.py

from __future__ import annotations

from typing import Protocol

from evaluator.character_statistics import CharacterStatistics
from evaluator.transition_statistics import TransitionStatistics
from evaluator.trigram_statistics import TrigramStatistics
from models.layout import Layout
from models.multi_start_optimization_result import (
    MultiStartOptimizationResult,
)
from models.optimization_result import OptimizationResult


class LocalOptimizer(Protocol):
    def optimize(
        self,
        layout: Layout,
        transition_statistics: TransitionStatistics,
        character_statistics: CharacterStatistics,
        trigram_statistics: TrigramStatistics | None = None,
    ) -> OptimizationResult: ...


class StartLayoutFactory(Protocol):
    def create(
        self,
        base_layout: Layout,
        run_index: int,
    ) -> Layout: ...


class MultiStartOptimizer:
    """
    Run independent local searches from multiple
    generated starting layouts.
    """

    def __init__(
        self,
        local_optimizer: LocalOptimizer,
        start_layout_factory: StartLayoutFactory,
        runs: int,
    ) -> None:
        if runs < 1:
            raise ValueError(
                "runs must be greater than or equal to 1"
            )

        self._local_optimizer = local_optimizer
        self._start_layout_factory = (
            start_layout_factory
        )
        self._runs = runs

    @property
    def runs(self) -> int:
        return self._runs

    def optimize(
        self,
        layout: Layout,
        transition_statistics: TransitionStatistics,
        character_statistics: CharacterStatistics,
        trigram_statistics: TrigramStatistics | None = None,
    ) -> MultiStartOptimizationResult:
        results: list[
            OptimizationResult
        ] = []

        for run_index in range(self._runs):
            start_layout = (
                self._start_layout_factory.create(
                    base_layout=layout,
                    run_index=run_index,
                )
            )

            result = self._local_optimizer.optimize(
                layout=start_layout,
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

            results.append(result)

        return MultiStartOptimizationResult(
            results=tuple(results)
        )
