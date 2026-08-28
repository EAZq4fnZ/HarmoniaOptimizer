# tests/test_fast_finger_load_score_evaluator.py

from __future__ import annotations

import pytest

from evaluator.character_statistics import (
    CharacterStatistics,
)
from evaluator.fast_finger_load_score_evaluator import (
    FastFingerLoadScoreEvaluator,
)
from evaluator.finger_load_pipeline import (
    FingerLoadPipeline,
)
from models.enums import Finger, Hand
from models.finger_load_budget import (
    FingerLoadBudget,
)
from models.layout import Layout


def make_layout() -> Layout:
    return Layout(
        name="test",
        description="Fast finger-load evaluator test layout",
        version="1.0",
        layer="L0",
        mapping={
            "A": "L-I-H-3",
            "B": "L-M-H-2",
            "C": "L-R-H-1",
            "D": "L-P-H-1",
            "E": "R-I-H-3",
            "F": "R-M-H-2",
            "G": "R-R-H-1",
            "H": "R-P-H-1",
            "I": "L-I-T-3",
            "J": "L-M-T-2",
            "K": "L-R-T-1",
            "L": "L-P-T-1",
            "M": "R-I-T-3",
            "N": "R-M-T-2",
            "O": "R-R-T-1",
            "P": "R-P-T-1",
            "Q": "L-I-B-3",
            "R": "L-M-B-2",
            "S": "L-R-B-1",
            "T": "L-P-B-1",
            "U": "R-I-B-3",
            "V": "R-M-B-2",
            "W": "R-R-B-1",
            "X": "R-P-B-1",
            "Y": "L-I-H-4",
            "Z": "R-I-H-4",
        },
    )


def make_budgets() -> tuple[FingerLoadBudget, ...]:
    return (
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.PINKY,
            target_ratio=0.10,
            tolerance=0.02,
        ),
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.RING,
            target_ratio=0.10,
            tolerance=0.02,
        ),
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.MIDDLE,
            target_ratio=0.15,
            tolerance=0.02,
        ),
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            target_ratio=0.15,
            tolerance=0.02,
        ),
        FingerLoadBudget(
            hand=Hand.RIGHT,
            finger=Finger.INDEX,
            target_ratio=0.15,
            tolerance=0.02,
        ),
        FingerLoadBudget(
            hand=Hand.RIGHT,
            finger=Finger.MIDDLE,
            target_ratio=0.15,
            tolerance=0.02,
        ),
        FingerLoadBudget(
            hand=Hand.RIGHT,
            finger=Finger.RING,
            target_ratio=0.10,
            tolerance=0.02,
        ),
        FingerLoadBudget(
            hand=Hand.RIGHT,
            finger=Finger.PINKY,
            target_ratio=0.10,
            tolerance=0.02,
        ),
    )


def make_statistics(
    counts: dict[str, int],
) -> CharacterStatistics:
    statistics = CharacterStatistics()

    statistics.add(
        counts
    )

    return statistics


def normal_finger_load_score(
    layout: Layout,
    statistics: CharacterStatistics,
    budgets: tuple[FingerLoadBudget, ...],
) -> float:
    evaluations = FingerLoadPipeline().evaluate(
        layout=layout,
        statistics=statistics,
        budgets=budgets,
    )

    return sum(
        evaluation.penalty
        for evaluation in evaluations
    )


def test_fast_evaluator_returns_float() -> None:
    evaluator = FastFingerLoadScoreEvaluator(
        make_budgets()
    )

    result = evaluator.evaluate(
        make_layout(),
        make_statistics(
            {
                "A": 10,
                "B": 20,
                "E": 30,
                "F": 40,
            }
        ),
    )

    assert isinstance(
        result,
        float,
    )


def test_fast_evaluator_matches_pipeline() -> None:
    layout = make_layout()
    budgets = make_budgets()

    statistics = make_statistics(
        {
            "A": 10,
            "B": 20,
            "D": 30,
            "N": 40,
            "P": 25,
        }
    )

    normal = normal_finger_load_score(
        layout,
        statistics,
        budgets,
    )

    fast = FastFingerLoadScoreEvaluator(
        budgets
    ).evaluate(
        layout,
        statistics,
    )

    assert fast == pytest.approx(
        normal
    )


def test_fast_evaluator_matches_after_layout_change() -> None:
    budgets = make_budgets()

    statistics = make_statistics(
        {
            "A": 50,
            "D": 10,
            "E": 20,
            "H": 40,
        }
    )

    first_layout = make_layout()

    second_mapping = dict(
        first_layout.mapping
    )

    second_mapping["A"], second_mapping["H"] = (
        second_mapping["H"],
        second_mapping["A"],
    )

    second_layout = Layout(
        name="test-swapped",
        description=(
            "Fast finger-load evaluator swapped test layout"
        ),
        version="1.0",
        layer="L0",
        mapping=second_mapping,
    )

    evaluator = FastFingerLoadScoreEvaluator(
        budgets
    )

    first_fast = evaluator.evaluate(
        first_layout,
        statistics,
    )

    first_normal = normal_finger_load_score(
        first_layout,
        statistics,
        budgets,
    )

    second_fast = evaluator.evaluate(
        second_layout,
        statistics,
    )

    second_normal = normal_finger_load_score(
        second_layout,
        statistics,
        budgets,
    )

    assert first_fast == pytest.approx(
        first_normal
    )

    assert second_fast == pytest.approx(
        second_normal
    )


def test_fast_evaluator_handles_empty_statistics() -> None:
    evaluator = FastFingerLoadScoreEvaluator(
        make_budgets()
    )

    result = evaluator.evaluate(
        make_layout(),
        CharacterStatistics(),
    )

    assert result == 0.0


def test_fast_evaluator_ignores_missing_characters() -> None:
    layout = make_layout()
    budgets = make_budgets()

    statistics = make_statistics(
        {
            "A": 10,
            "!": 100,
            "?": 200,
        }
    )

    normal = normal_finger_load_score(
        layout,
        statistics,
        budgets,
    )

    fast = FastFingerLoadScoreEvaluator(
        budgets
    ).evaluate(
        layout,
        statistics,
    )

    assert fast == pytest.approx(
        normal
    )


def test_fast_evaluator_handles_no_excess_load() -> None:
    layout = make_layout()

    budgets = (
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            target_ratio=1.0,
            tolerance=0.0,
        ),
    )

    statistics = make_statistics(
        {
            "A": 10,
            "E": 10,
        }
    )

    result = FastFingerLoadScoreEvaluator(
        budgets
    ).evaluate(
        layout,
        statistics,
    )

    assert result == 0.0


def test_fast_evaluator_applies_excess_penalty() -> None:
    layout = make_layout()

    budgets = (
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            target_ratio=0.10,
            tolerance=0.0,
        ),
    )

    statistics = make_statistics(
        {
            "A": 100,
            "E": 100,
        }
    )

    normal = normal_finger_load_score(
        layout,
        statistics,
        budgets,
    )

    fast = FastFingerLoadScoreEvaluator(
        budgets
    ).evaluate(
        layout,
        statistics,
    )

    assert fast == pytest.approx(
        normal
    )


def test_fast_evaluator_reuses_position_pair_cache() -> None:
    evaluator = FastFingerLoadScoreEvaluator(
        make_budgets()
    )

    layout = make_layout()

    statistics = make_statistics(
        {
            "A": 10,
            "B": 20,
            "E": 30,
            "F": 40,
        }
    )

    first = evaluator.evaluate(
        layout,
        statistics,
    )

    cache_size_after_first = len(
        evaluator._position_pair_cache
    )

    second = evaluator.evaluate(
        layout,
        statistics,
    )

    cache_size_after_second = len(
        evaluator._position_pair_cache
    )

    assert first == pytest.approx(
        second
    )

    assert (
        cache_size_after_second
        == cache_size_after_first
    )


def test_evaluate_mapping_matches_evaluate() -> None:
    layout = make_layout()
    budgets = make_budgets()

    statistics = make_statistics(
        {
            "A": 10,
            "B": 20,
            "D": 30,
            "N": 40,
            "P": 25,
        }
    )

    evaluator = FastFingerLoadScoreEvaluator(
        budgets
    )

    layout_result = evaluator.evaluate(
        layout,
        statistics,
    )

    mapping_result = evaluator.evaluate_mapping(
        layout.mapping,
        statistics,
    )

    assert mapping_result == pytest.approx(
        layout_result
    )


def test_evaluate_indexed_matches_evaluate() -> None:
    layout = make_layout()
    budgets = make_budgets()

    statistics = make_statistics(
        {
            "A": 10,
            "B": 20,
            "D": 30,
            "N": 40,
            "P": 25,
        }
    )

    evaluator = FastFingerLoadScoreEvaluator(
        budgets
    )

    layout_result = evaluator.evaluate(
        layout,
        statistics,
    )

    positions = tuple(
        layout.position(
            chr(ord("A") + index)
        )
        for index in range(26)
    )

    indexed_result = evaluator.evaluate_indexed(
        positions,
        statistics,
    )

    assert indexed_result == pytest.approx(
        layout_result
    )


def test_evaluate_position_indexed_matches_evaluate() -> None:
    layout = make_layout()
    budgets = make_budgets()

    statistics = make_statistics(
        {
            "A": 10,
            "B": 20,
            "D": 30,
            "N": 40,
            "P": 25,
        }
    )

    evaluator = FastFingerLoadScoreEvaluator(
        budgets
    )

    normal_result = evaluator.evaluate(
        layout,
        statistics,
    )

    string_positions: list[str | None] = [
        None
    ] * 26

    for letter, position in layout.mapping.items():
        index = (
            ord(letter)
            - ord("A")
        )

        string_positions[index] = position

    unique_positions = tuple(
        layout.mapping.values()
    )

    position_indexes = {
        position: index
        for index, position
        in enumerate(unique_positions)
    }

    integer_positions = tuple(
        position_indexes[position]
        for position in string_positions
        if position is not None
    )

    (
        position_finger_indexes,
        allowed_ratios,
    ) = evaluator.build_position_finger_index(
        unique_positions,
        position_indexes,
    )

    indexed_result = (
        evaluator.evaluate_position_indexed(
            integer_positions,
            position_finger_indexes,
            allowed_ratios,
            statistics,
        )
    )

    assert indexed_result == pytest.approx(
        normal_result
    )

def test_evaluate_prepared_position_indexed_complete_matches_position_indexed(
) -> None:
    layout = make_layout()
    budgets = make_budgets()

    statistics = make_statistics(
        {
            "A": 10,
            "B": 20,
            "D": 30,
            "N": 40,
            "P": 25,
        }
    )

    evaluator = FastFingerLoadScoreEvaluator(
        budgets
    )

    string_positions = tuple(
        layout.position(
            chr(ord("A") + index)
        )
        for index in range(26)
    )

    unique_positions = tuple(
        layout.mapping.values()
    )

    position_indexes = {
        position: index
        for index, position
        in enumerate(unique_positions)
    }

    integer_positions = tuple(
        position_indexes[position]
        for position in string_positions
        if position is not None
    )

    (
        position_finger_indexes,
        allowed_ratios,
    ) = evaluator.build_position_finger_index(
        unique_positions,
        position_indexes,
    )

    normal_result = (
        evaluator.evaluate_position_indexed(
            integer_positions,
            position_finger_indexes,
            allowed_ratios,
            statistics,
        )
    )

    (
        weighted_statistics,
        total_weighted_load,
    ) = evaluator.prepare_position_indexed_statistics(
        statistics
    )

    prepared_result = (
        evaluator
        .evaluate_prepared_position_indexed_complete(
            integer_positions,
            position_finger_indexes,
            allowed_ratios,
            weighted_statistics,
            total_weighted_load,
        )
    )

    assert prepared_result == pytest.approx(
        normal_result
    )


def test_evaluate_prepared_position_indexed_complete_handles_empty_statistics(
) -> None:
    layout = make_layout()

    evaluator = FastFingerLoadScoreEvaluator(
        make_budgets()
    )

    statistics = CharacterStatistics()

    string_positions = tuple(
        layout.position(
            chr(ord("A") + index)
        )
        for index in range(26)
    )

    unique_positions = tuple(
        layout.mapping.values()
    )

    position_indexes = {
        position: index
        for index, position
        in enumerate(unique_positions)
    }

    integer_positions = tuple(
        position_indexes[position]
        for position in string_positions
        if position is not None
    )

    (
        position_finger_indexes,
        allowed_ratios,
    ) = evaluator.build_position_finger_index(
        unique_positions,
        position_indexes,
    )

    (
        weighted_statistics,
        total_weighted_load,
    ) = evaluator.prepare_position_indexed_statistics(
        statistics
    )

    result = (
        evaluator
        .evaluate_prepared_position_indexed_complete(
            integer_positions,
            position_finger_indexes,
            allowed_ratios,
            weighted_statistics,
            total_weighted_load,
        )
    )

    assert result == 0.0