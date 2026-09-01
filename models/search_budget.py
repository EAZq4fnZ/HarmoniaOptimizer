# models/search_budget.py

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SearchBudget:
    runs: int
    max_iterations: int

    def __post_init__(self) -> None:
        if self.runs < 1:
            raise ValueError(
                "runs must be greater than or equal to 1"
            )

        if self.max_iterations < 0:
            raise ValueError(
                "max_iterations must be greater "
                "than or equal to 0"
            )
