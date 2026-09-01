import pytest

from models.search_budget import SearchBudget
from models.search_budget_profiles import SearchBudgetProfiles
from models.search_mode import SearchMode


def make_profiles() -> SearchBudgetProfiles:
    return SearchBudgetProfiles(
        fast=SearchBudget(
            runs=2,
            max_iterations=10,
        ),
        standard=SearchBudget(
            runs=5,
            max_iterations=20,
        ),
        deep=SearchBudget(
            runs=10,
            max_iterations=30,
        ),
    )


def test_search_mode_values() -> None:
    assert SearchMode.FAST.value == "fast"
    assert SearchMode.STANDARD.value == "standard"
    assert SearchMode.DEEP.value == "deep"


def test_returns_fast_budget() -> None:
    profiles = make_profiles()

    assert profiles.for_mode(
        SearchMode.FAST
    ) == profiles.fast


def test_returns_standard_budget() -> None:
    profiles = make_profiles()

    assert profiles.for_mode(
        SearchMode.STANDARD
    ) == profiles.standard


def test_returns_deep_budget() -> None:
    profiles = make_profiles()

    assert profiles.for_mode(
        SearchMode.DEEP
    ) == profiles.deep


def test_profiles_are_immutable() -> None:
    profiles = make_profiles()

    with pytest.raises(
        AttributeError,
    ):
        profiles.fast = SearchBudget(
            runs=99,
            max_iterations=99,
        )
