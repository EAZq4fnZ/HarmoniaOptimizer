# models/search_budget_profiles.py

from __future__ import annotations

from dataclasses import dataclass

from models.search_budget import SearchBudget
from models.search_mode import SearchMode


@dataclass(frozen=True, slots=True)
class SearchBudgetProfiles:
    fast: SearchBudget
    standard: SearchBudget
    deep: SearchBudget

    def for_mode(
        self,
        mode: SearchMode,
    ) -> SearchBudget:
        if mode is SearchMode.FAST:
            return self.fast

        if mode is SearchMode.STANDARD:
            return self.standard

        if mode is SearchMode.DEEP:
            return self.deep

        raise ValueError(
            f"Unsupported search mode: {mode!r}"
        )
