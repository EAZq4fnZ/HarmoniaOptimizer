import json

import pytest

from config_loader.search_budget_profiles_loader import (
    SearchBudgetProfilesLoader,
)
from models.search_budget import SearchBudget


def make_data() -> dict:
    return {
        "fast": {
            "runs": 2,
            "max_iterations": 10,
        },
        "standard": {
            "runs": 5,
            "max_iterations": 20,
        },
        "deep": {
            "runs": 10,
            "max_iterations": 30,
        },
    }


def test_from_dict() -> None:
    profiles = SearchBudgetProfilesLoader.from_dict(
        make_data()
    )

    assert profiles.fast == SearchBudget(
        runs=2,
        max_iterations=10,
    )
    assert profiles.standard == SearchBudget(
        runs=5,
        max_iterations=20,
    )
    assert profiles.deep == SearchBudget(
        runs=10,
        max_iterations=30,
    )


def test_load(tmp_path) -> None:
    path = tmp_path / "search.json"

    path.write_text(
        json.dumps(make_data()),
        encoding="utf-8",
    )

    profiles = SearchBudgetProfilesLoader.load(
        path
    )

    assert profiles.fast.runs == 2
    assert profiles.standard.runs == 5
    assert profiles.deep.runs == 10


def test_invalid_runs_are_rejected() -> None:
    data = make_data()
    data["fast"]["runs"] = 0

    with pytest.raises(
        ValueError,
        match="runs",
    ):
        SearchBudgetProfilesLoader.from_dict(
            data
        )


def test_invalid_max_iterations_are_rejected() -> None:
    data = make_data()
    data["deep"]["max_iterations"] = -1

    with pytest.raises(
        ValueError,
        match="max_iterations",
    ):
        SearchBudgetProfilesLoader.from_dict(
            data
        )

def test_load_default_search_config() -> None:
    profiles = SearchBudgetProfilesLoader.load(
        "config/search/default.json"
    )

    assert profiles.fast == SearchBudget(
        runs=2,
        max_iterations=20,
    )
    assert profiles.standard == SearchBudget(
        runs=8,
        max_iterations=30,
    )
    assert profiles.deep == SearchBudget(
        runs=16,
        max_iterations=30,
    )


@pytest.mark.parametrize(
    ("key", "value"),
    (
        ("runs", 2.5),
        ("runs", "2"),
        ("runs", True),
        ("max_iterations", 10.5),
        ("max_iterations", "10"),
        ("max_iterations", False),
    ),
)
def test_non_integer_budget_value_is_rejected(
    key,
    value,
) -> None:
    data = make_data()
    data["fast"][key] = value

    with pytest.raises(
        TypeError,
        match=key,
    ):
        SearchBudgetProfilesLoader.from_dict(
            data
        )
