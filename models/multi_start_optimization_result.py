# models/multi_start_optimization_result.py

from __future__ import annotations

from dataclasses import dataclass

from models.optimization_result import OptimizationResult


@dataclass(slots=True, frozen=True)
class MultiStartOptimizationResult:
    """
    Aggregate result of multiple independent
    optimization runs.
    """

    results: tuple[OptimizationResult, ...]

    def __post_init__(self) -> None:
        if not self.results:
            raise ValueError(
                "results must not be empty"
            )

    @property
    def run_count(self) -> int:
        return len(self.results)

    @property
    def best_result(
        self,
    ) -> OptimizationResult | None:
        valid_results = (
            result
            for result in self.results
            if result.final_score is not None
        )

        return min(
            valid_results,
            key=lambda result: result.final_score,
            default=None,
        )

    @property
    def best_score(self) -> float | None:
        best = self.best_result

        if best is None:
            return None

        return best.final_score
