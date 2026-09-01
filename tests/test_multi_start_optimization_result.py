from __future__ import annotations

from models.multi_start_optimization_result import (
    MultiStartOptimizationResult,
)


class FakeResult:
    def __init__(
        self,
        final_score: float | None,
    ) -> None:
        self.final_score = final_score


def test_requires_at_least_one_result() -> None:
    try:
        MultiStartOptimizationResult(
            results=(),
        )
    except ValueError as exc:
        assert (
            str(exc)
            == "results must not be empty"
        )
    else:
        raise AssertionError(
            "Expected ValueError."
        )


def test_run_count() -> None:
    result = MultiStartOptimizationResult(
        results=(
            FakeResult(3.0),
            FakeResult(2.0),
            FakeResult(1.0),
        )
    )

    assert result.run_count == 3


def test_best_result_is_lowest_score() -> None:
    first = FakeResult(3.0)
    second = FakeResult(1.0)
    third = FakeResult(2.0)

    result = MultiStartOptimizationResult(
        results=(
            first,
            second,
            third,
        )
    )

    assert result.best_result is second
    assert result.best_score == 1.0


def test_best_result_ignores_none_scores() -> None:
    invalid = FakeResult(None)
    valid = FakeResult(2.0)

    result = MultiStartOptimizationResult(
        results=(
            invalid,
            valid,
        )
    )

    assert result.best_result is valid
    assert result.best_score == 2.0


def test_best_result_is_none_when_all_scores_none() -> None:
    result = MultiStartOptimizationResult(
        results=(
            FakeResult(None),
            FakeResult(None),
        )
    )

    assert result.best_result is None
    assert result.best_score is None
