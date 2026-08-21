# models/optimization_result.py

from __future__ import annotations

from dataclasses import dataclass

from models.candidate_evaluation import CandidateEvaluation
from models.optimization_step import OptimizationStep


@dataclass(slots=True, frozen=True)
class OptimizationResult:
    """
    Result of a complete optimization run.
    """

    initial_evaluation: CandidateEvaluation
    final_evaluation: CandidateEvaluation
    steps: tuple[OptimizationStep, ...]

    @property
    def initial_score(self) -> float | None:
        return self.initial_evaluation.score

    @property
    def final_score(self) -> float | None:
        return self.final_evaluation.score

    @property
    def iteration_count(self) -> int:
        return len(self.steps)

    @property
    def improved(self) -> bool:
        if self.initial_score is None:
            return False

        if self.final_score is None:
            return False

        return self.final_score < self.initial_score

    @property
    def improvement(self) -> float | None:
        if self.initial_score is None:
            return None

        if self.final_score is None:
            return None

        return self.initial_score - self.final_score