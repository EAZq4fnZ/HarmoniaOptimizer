from dataclasses import FrozenInstanceError

import pytest

from models.search_budget import SearchBudget


def test_attributes() -> None:
    budget = SearchBudget(
        runs=20,
        max_iterations=100,
    )

    assert budget.runs == 20
    assert budget.max_iterations == 100


def test_is_immutable() -> None:
    budget = SearchBudget(
        runs=20,
        max_iterations=100,
    )

    with pytest.raises(FrozenInstanceError):
        budget.runs = 30


def test_rejects_zero_runs() -> None:
    with pytest.raises(
        ValueError,
        match="runs",
    ):
        SearchBudget(
            runs=0,
            max_iterations=100,
        )


def test_rejects_negative_runs() -> None:
    with pytest.raises(
        ValueError,
        match="runs",
    ):
        SearchBudget(
            runs=-1,
            max_iterations=100,
        )


def test_allows_zero_max_iterations() -> None:
    budget = SearchBudget(
        runs=20,
        max_iterations=0,
    )

    assert budget.max_iterations == 0


def test_rejects_negative_max_iterations() -> None:
    with pytest.raises(
        ValueError,
        match="max_iterations",
    ):
        SearchBudget(
            runs=20,
            max_iterations=-1,
        )
