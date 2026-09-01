# config_loader/search_budget_profiles_loader.py

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from models.search_budget import SearchBudget
from models.search_budget_profiles import SearchBudgetProfiles


class SearchBudgetProfilesLoader:
    """
    Load SearchBudgetProfiles from a JSON file.
    """

    @classmethod
    def load(
        cls,
        path: str | Path,
    ) -> SearchBudgetProfiles:
        path = Path(path)

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return cls.from_dict(data)

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> SearchBudgetProfiles:
        return SearchBudgetProfiles(
            fast=cls._parse_budget(
                data["fast"]
            ),
            standard=cls._parse_budget(
                data["standard"]
            ),
            deep=cls._parse_budget(
                data["deep"]
            ),
        )

    @classmethod
    def _parse_budget(
        cls,
        data: dict[str, Any],
    ) -> SearchBudget:
        return SearchBudget(
            runs=cls._parse_integer(
                data["runs"],
                name="runs",
            ),
            max_iterations=cls._parse_integer(
                data["max_iterations"],
                name="max_iterations",
            ),
        )

    @staticmethod
    def _parse_integer(
        value: Any,
        *,
        name: str,
    ) -> int:
        if type(value) is not int:
            raise TypeError(
                f"{name} must be an integer"
            )

        return value
