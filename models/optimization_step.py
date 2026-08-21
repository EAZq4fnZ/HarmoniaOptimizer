# models/optimization_step.py

from __future__ import annotations

from dataclasses import dataclass

from models.candidate_evaluation import CandidateEvaluation


@dataclass(slots=True, frozen=True)
class OptimizationStep:
    """
    One accepted improvement during optimization.
    """

    iteration: int
    evaluation: CandidateEvaluation

    def __post_init__(self) -> None:
        if self.iteration < 1:
            raise ValueError(
                "iteration must be greater than or equal to 1"
            )

    @property
    def score(self) -> float | None:
        return self.evaluation.score