# tests/test_fast_layout_score_evaluator.py

from __future__ import annotations

import pytest

from evaluator.fast_layout_score_evaluator import (
    FastLayoutScoreEvaluator,
)
from evaluator.layout_evaluator import LayoutEvaluator
from evaluator.transition_statistics import (
    TransitionStatistics,
)
from models.layout import Layout
from models.transition_cost import (
    TransitionCostWeights,
)


def make_layout() -> Layout:
    return Layout(
        name="test",
        description="Fast layout evaluator test layout",
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


def make_weights() -> TransitionCostWeights:
    return TransitionCostWeights(
        same_finger_penalty=2.0,
        same_hand_penalty=1.0,
        row_change_penalty=0.5,
        alternation_reward=0.25,
        inward_roll_reward=0.4,
        outward_roll_reward=0.2,
    )


def make_statistics() -> TransitionStatistics:
    statistics = TransitionStatistics()

    statistics.add(
        {
            ("A", "B"): 10,
            ("B", "A"): 7,
            ("A", "E"): 12,
            ("A", "I"): 4,
            ("E", "F"): 8,
            ("F", "E"): 6,
            ("Y", "Z"): 3,
            ("Q", "U"): 5,
        }
    )

    return statistics


def test_fast_evaluator_returns_aggregate_values() -> None:
    evaluator = FastLayoutScoreEvaluator(
        make_weights()
    )

    result = evaluator.evaluate(
        make_layout(),
        make_statistics(),
    )

    assert isinstance(
        result.total_cost,
        float,
    )

    assert result.evaluated_weight > 0.0
    assert result.skipped_weight >= 0.0


def test_fast_evaluator_matches_layout_evaluator() -> None:
    layout = make_layout()
    statistics = make_statistics()
    weights = make_weights()

    normal = LayoutEvaluator(
        weights
    ).evaluate(
        layout,
        statistics,
    )

    fast = FastLayoutScoreEvaluator(
        weights
    ).evaluate(
        layout,
        statistics,
    )

    assert fast.total_cost == pytest.approx(
        normal.total_cost
    )

    assert (
        fast.evaluated_weight
        == pytest.approx(
            normal.evaluated_weight
        )
    )

    assert (
        fast.skipped_weight
        == pytest.approx(
            normal.skipped_weight
        )
    )


def test_fast_evaluator_matches_after_layout_change() -> None:
    statistics = make_statistics()
    weights = make_weights()

    first_mapping = dict(
        make_layout().mapping
    )

    second_mapping = dict(
        first_mapping
    )

    second_mapping["A"], second_mapping["E"] = (
        second_mapping["E"],
        second_mapping["A"],
    )

    second_layout = Layout(
        name="test-swapped",
        description=(
            "Fast layout evaluator swapped test layout"
        ),
        version="1.0",
        layer="L0",
        mapping=second_mapping,
    )

    normal_evaluator = LayoutEvaluator(
        weights
    )

    fast_evaluator = FastLayoutScoreEvaluator(
        weights
    )

    normal_first = normal_evaluator.evaluate(
        make_layout(),
        statistics,
    )

    fast_first = fast_evaluator.evaluate(
        make_layout(),
        statistics,
    )

    normal_second = normal_evaluator.evaluate(
        second_layout,
        statistics,
    )

    fast_second = fast_evaluator.evaluate(
        second_layout,
        statistics,
    )

    assert (
        fast_first.total_cost
        == pytest.approx(
            normal_first.total_cost
        )
    )

    assert (
        fast_second.total_cost
        == pytest.approx(
            normal_second.total_cost
        )
    )


def test_fast_evaluator_matches_all_transition_types() -> None:
    layout = make_layout()
    weights = make_weights()

    statistics = TransitionStatistics()

    statistics.add(
        {
            # Same hand, adjacent fingers.
            ("A", "B"): 3,

            # Reverse roll direction.
            ("B", "A"): 4,

            # Alternating hands.
            ("A", "E"): 5,

            # Same finger, different row.
            ("A", "I"): 6,

            # Same row.
            ("E", "F"): 7,

            # Extra index column.
            ("Y", "Z"): 8,
        }
    )

    normal = LayoutEvaluator(
        weights
    ).evaluate(
        layout,
        statistics,
    )

    fast = FastLayoutScoreEvaluator(
        weights
    ).evaluate(
        layout,
        statistics,
    )

    assert fast.total_cost == pytest.approx(
        normal.total_cost
    )

    assert (
        fast.evaluated_weight
        == pytest.approx(
            normal.evaluated_weight
        )
    )

    assert (
        fast.skipped_weight
        == pytest.approx(
            normal.skipped_weight
        )
    )


def test_fast_evaluator_reuses_transition_cost_cache() -> None:
    evaluator = FastLayoutScoreEvaluator(
        make_weights()
    )

    layout = make_layout()
    statistics = make_statistics()

    first = evaluator.evaluate(
        layout,
        statistics,
    )

    cache_size_after_first = len(
        evaluator._transition_cost_cache
    )

    second = evaluator.evaluate(
        layout,
        statistics,
    )

    cache_size_after_second = len(
        evaluator._transition_cost_cache
    )

    assert first == second

    assert (
        cache_size_after_second
        == cache_size_after_first
    )


def test_fast_evaluator_handles_empty_statistics() -> None:
    evaluator = FastLayoutScoreEvaluator(
        make_weights()
    )

    result = evaluator.evaluate(
        make_layout(),
        TransitionStatistics(),
    )

    assert result.total_cost == 0.0
    assert result.evaluated_weight == 0.0
    assert result.skipped_weight == 0.0


def test_evaluate_mapping_matches_evaluate() -> None:
    layout = make_layout()
    statistics = make_statistics()

    evaluator = FastLayoutScoreEvaluator(
        make_weights()
    )

    layout_result = evaluator.evaluate(
        layout,
        statistics,
    )

    mapping_result = evaluator.evaluate_mapping(
        layout.mapping,
        statistics,
    )

    assert (
        mapping_result.total_cost
        == pytest.approx(
            layout_result.total_cost
        )
    )

    assert (
        mapping_result.evaluated_weight
        == pytest.approx(
            layout_result.evaluated_weight
        )
    )

    assert (
        mapping_result.skipped_weight
        == pytest.approx(
            layout_result.skipped_weight
        )
    )


def test_evaluate_indexed_matches_evaluate() -> None:
    layout = make_layout()
    statistics = make_statistics()

    evaluator = FastLayoutScoreEvaluator(
        make_weights()
    )

    layout_result = evaluator.evaluate(
        layout,
        statistics,
    )

    positions: list[str | None] = [
        None
    ] * 26

    for letter, position in layout.mapping.items():
        index = (
            ord(letter.upper())
            - ord("A")
        )

        if 0 <= index < 26:
            positions[index] = position

    indexed_result = evaluator.evaluate_indexed(
        positions,
        statistics,
    )

    assert (
        indexed_result.total_cost
        == pytest.approx(
            layout_result.total_cost
        )
    )

    assert (
        indexed_result.evaluated_weight
        == pytest.approx(
            layout_result.evaluated_weight
        )
    )

    assert (
        indexed_result.skipped_weight
        == pytest.approx(
            layout_result.skipped_weight
        )
    )


def test_evaluate_position_indexed_matches_evaluate() -> None:
    layout = make_layout()
    statistics = make_statistics()

    evaluator = FastLayoutScoreEvaluator(
        make_weights()
    )

    normal_result = evaluator.evaluate(
        layout,
        statistics,
    )

    positions: list[str | None] = [
        None
    ] * 26

    for letter, position in layout.mapping.items():
        index = (
            ord(letter)
            - ord("A")
        )

        positions[index] = position

    (
        position_indexes,
        cost_matrix,
    ) = evaluator.build_position_index(
        tuple(
            layout.mapping.values()
        )
    )

    indexed_positions = (
        evaluator.convert_to_position_indexes(
            positions,
            position_indexes,
        )
    )

    indexed_result = (
        evaluator.evaluate_position_indexed(
            indexed_positions,
            cost_matrix,
            statistics,
        )
    )

    assert (
        indexed_result.total_cost
        == pytest.approx(
            normal_result.total_cost
        )
    )

    assert (
        indexed_result.evaluated_weight
        == pytest.approx(
            normal_result.evaluated_weight
        )
    )

    assert (
        indexed_result.skipped_weight
        == pytest.approx(
            normal_result.skipped_weight
        )
    )


def test_position_indexed_delta_matches_full_evaluation() -> None:
    layout = make_layout()
    statistics = make_statistics()

    evaluator = FastLayoutScoreEvaluator(
        make_weights()
    )

    string_positions: list[str | None] = [
        None
    ] * 26

    for letter, position in layout.mapping.items():
        index = (
            ord(letter.upper())
            - ord("A")
        )

        if 0 <= index < 26:
            string_positions[index] = position

    logical_positions = tuple(
        position
        for position in string_positions
        if position is not None
    )

    (
        position_indexes,
        cost_matrix,
    ) = evaluator.build_position_index(
        logical_positions
    )

    base_positions = list(
        evaluator.convert_to_position_indexes(
            string_positions,
            position_indexes,
        )
    )

    baseline = (
        evaluator.prepare_position_indexed_delta(
            base_positions,
            cost_matrix,
            statistics,
        )
    )

    candidate_positions = list(
        base_positions
    )

    a_index = ord("A") - ord("A")
    e_index = ord("E") - ord("A")

    (
        candidate_positions[a_index],
        candidate_positions[e_index],
    ) = (
        candidate_positions[e_index],
        candidate_positions[a_index],
    )

    full_result = (
        evaluator.evaluate_position_indexed(
            candidate_positions,
            cost_matrix,
            statistics,
        )
    )

    delta_result = (
        evaluator.evaluate_position_indexed_delta(
            candidate_positions,
            cost_matrix,
            statistics,
            baseline,
            (
                a_index,
                e_index,
            ),
        )
    )

    assert delta_result.total_cost == pytest.approx(
        full_result.total_cost
    )

    assert (
        delta_result.evaluated_weight
        == pytest.approx(
            full_result.evaluated_weight
        )
    )

    assert (
        delta_result.skipped_weight
        == pytest.approx(
            full_result.skipped_weight
        )
    )


def test_position_indexed_delta_without_changes_matches_baseline() -> None:
    layout = make_layout()
    statistics = make_statistics()

    evaluator = FastLayoutScoreEvaluator(
        make_weights()
    )

    string_positions: list[str | None] = [
        None
    ] * 26

    for letter, position in layout.mapping.items():
        index = (
            ord(letter.upper())
            - ord("A")
        )

        if 0 <= index < 26:
            string_positions[index] = position

    logical_positions = tuple(
        position
        for position in string_positions
        if position is not None
    )

    (
        position_indexes,
        cost_matrix,
    ) = evaluator.build_position_index(
        logical_positions
    )

    base_positions = list(
        evaluator.convert_to_position_indexes(
            string_positions,
            position_indexes,
        )
    )

    baseline = (
        evaluator.prepare_position_indexed_delta(
            base_positions,
            cost_matrix,
            statistics,
        )
    )

    result = (
        evaluator.evaluate_position_indexed_delta(
            base_positions,
            cost_matrix,
            statistics,
            baseline,
            (),
        )
    )

    assert result.total_cost == pytest.approx(
        baseline.total_cost
    )

    assert (
        result.evaluated_weight
        == pytest.approx(
            baseline.evaluated_weight
        )
    )

    assert (
        result.skipped_weight
        == pytest.approx(
            baseline.skipped_weight
        )
    )


def test_evaluate_position_indexed_flat_matches_evaluate() -> None:
    layout = make_layout()
    statistics = make_statistics()

    evaluator = FastLayoutScoreEvaluator(
        make_weights()
    )

    string_positions: list[str | None] = [
        None
    ] * 26

    for letter, position in layout.mapping.items():
        index = (
            ord(letter.upper())
            - ord("A")
        )

        if 0 <= index < 26:
            string_positions[index] = position

    logical_positions = tuple(
        position
        for position in string_positions
        if position is not None
    )

    (
        position_indexes,
        flat_costs,
        position_count,
    ) = evaluator.build_flat_position_costs(
        logical_positions
    )

    integer_positions = (
        evaluator.convert_to_position_indexes(
            string_positions,
            position_indexes,
        )
    )

    flat_result = (
        evaluator.evaluate_position_indexed_flat(
            integer_positions,
            flat_costs,
            position_count,
            statistics,
        )
    )

    normal_result = (
        evaluator.evaluate(
            layout,
            statistics,
        )
    )

    assert (
        flat_result.total_cost
        == pytest.approx(
            normal_result.total_cost
        )
    )

    assert (
        flat_result.evaluated_weight
        == pytest.approx(
            normal_result.evaluated_weight
        )
    )

    assert (
        flat_result.skipped_weight
        == pytest.approx(
            normal_result.skipped_weight
        )
    )


def test_evaluate_prepared_position_indexed_matches_evaluate() -> None:
    layout = make_layout()
    statistics = make_statistics()

    evaluator = FastLayoutScoreEvaluator(
        make_weights()
    )

    string_positions: list[str | None] = [
        None
    ] * 26

    for letter, position in layout.mapping.items():
        index = (
            ord(letter.upper())
            - ord("A")
        )

        if 0 <= index < 26:
            string_positions[index] = position

    logical_positions = tuple(
        position
        for position in string_positions
        if position is not None
    )

    (
        position_indexes,
        cost_matrix,
    ) = evaluator.build_position_index(
        logical_positions
    )

    integer_positions = (
        evaluator.convert_to_position_indexes(
            string_positions,
            position_indexes,
        )
    )

    prepared = (
        evaluator.prepare_position_indexed_transitions(
            statistics
        )
    )

    prepared_result = (
        evaluator.evaluate_prepared_position_indexed(
            integer_positions,
            cost_matrix,
            prepared,
        )
    )

    normal_result = evaluator.evaluate(
        layout,
        statistics,
    )

    assert (
        prepared_result.total_cost
        == pytest.approx(
            normal_result.total_cost
        )
    )

    assert (
        prepared_result.evaluated_weight
        == pytest.approx(
            normal_result.evaluated_weight
        )
    )

    assert (
        prepared_result.skipped_weight
        == pytest.approx(
            normal_result.skipped_weight
        )
    )


def test_prepared_position_indexed_preserves_skipped_transitions() -> None:
    layout = make_layout()
    statistics = make_statistics()

    statistics.add(
        {
            ("?", "A"): 9,
            ("A", "?"): 11,
        }
    )

    evaluator = FastLayoutScoreEvaluator(
        make_weights()
    )

    string_positions: list[str | None] = [
        None
    ] * 26

    for letter, position in layout.mapping.items():
        index = (
            ord(letter.upper())
            - ord("A")
        )

        if 0 <= index < 26:
            string_positions[index] = position

    logical_positions = tuple(
        position
        for position in string_positions
        if position is not None
    )

    (
        position_indexes,
        cost_matrix,
    ) = evaluator.build_position_index(
        logical_positions
    )

    integer_positions = (
        evaluator.convert_to_position_indexes(
            string_positions,
            position_indexes,
        )
    )

    prepared = (
        evaluator.prepare_position_indexed_transitions(
            statistics
        )
    )

    prepared_result = (
        evaluator.evaluate_prepared_position_indexed(
            integer_positions,
            cost_matrix,
            prepared,
        )
    )

    full_result = evaluator.evaluate_position_indexed(
        integer_positions,
        cost_matrix,
        statistics,
    )

    assert (
        prepared_result.total_cost
        == pytest.approx(
            full_result.total_cost
        )
    )

    assert (
        prepared_result.evaluated_weight
        == pytest.approx(
            full_result.evaluated_weight
        )
    )

    assert (
        prepared_result.skipped_weight
        == pytest.approx(
            full_result.skipped_weight
        )
    )


def test_prepared_position_indexed_handles_missing_layout_letter() -> None:
    layout = make_layout()
    statistics = make_statistics()

    evaluator = FastLayoutScoreEvaluator(
        make_weights()
    )

    string_positions: list[str | None] = [
        None
    ] * 26

    for letter, position in layout.mapping.items():
        index = (
            ord(letter.upper())
            - ord("A")
        )

        if 0 <= index < 26:
            string_positions[index] = position

    logical_positions = tuple(
        position
        for position in string_positions
        if position is not None
    )

    (
        position_indexes,
        cost_matrix,
    ) = evaluator.build_position_index(
        logical_positions
    )

    integer_positions = list(
        evaluator.convert_to_position_indexes(
            string_positions,
            position_indexes,
        )
    )

    integer_positions[
        ord("A") - ord("A")
    ] = -1

    prepared = (
        evaluator.prepare_position_indexed_transitions(
            statistics
        )
    )

    prepared_result = (
        evaluator.evaluate_prepared_position_indexed(
            integer_positions,
            cost_matrix,
            prepared,
        )
    )

    full_result = evaluator.evaluate_position_indexed(
        integer_positions,
        cost_matrix,
        statistics,
    )

    assert (
        prepared_result.total_cost
        == pytest.approx(
            full_result.total_cost
        )
    )

    assert (
        prepared_result.evaluated_weight
        == pytest.approx(
            full_result.evaluated_weight
        )
    )

    assert (
        prepared_result.skipped_weight
        == pytest.approx(
            full_result.skipped_weight
        )
    )

def _prepare_prepared_delta_test_data():
    layout = make_layout()
    statistics = make_statistics()

    evaluator = FastLayoutScoreEvaluator(
        make_weights()
    )

    string_positions: list[str | None] = [
        None
    ] * 26

    for letter, position in layout.mapping.items():
        index = (
            ord(letter.upper())
            - ord("A")
        )

        if 0 <= index < 26:
            string_positions[index] = position

    logical_positions = tuple(
        position
        for position in string_positions
        if position is not None
    )

    (
        position_indexes,
        cost_matrix,
    ) = evaluator.build_position_index(
        logical_positions
    )

    base_positions = list(
        evaluator.convert_to_position_indexes(
            string_positions,
            position_indexes,
        )
    )

    prepared = (
        evaluator.prepare_position_indexed_transitions(
            statistics
        )
    )

    baseline = (
        evaluator
        .prepare_prepared_position_indexed_delta(
            base_positions,
            cost_matrix,
            prepared,
        )
    )

    return (
        evaluator,
        statistics,
        cost_matrix,
        base_positions,
        prepared,
        baseline,
    )


def test_prepared_position_indexed_delta_matches_prepared_full() -> None:
    (
        evaluator,
        _statistics,
        cost_matrix,
        base_positions,
        prepared,
        baseline,
    ) = _prepare_prepared_delta_test_data()

    candidate_positions = list(
        base_positions
    )

    a_index = ord("A") - ord("A")
    e_index = ord("E") - ord("A")

    (
        candidate_positions[a_index],
        candidate_positions[e_index],
    ) = (
        candidate_positions[e_index],
        candidate_positions[a_index],
    )

    full_result = (
        evaluator.evaluate_prepared_position_indexed(
            candidate_positions,
            cost_matrix,
            prepared,
        )
    )

    delta_result = (
        evaluator
        .evaluate_prepared_position_indexed_delta(
            candidate_positions,
            cost_matrix,
            baseline,
            (
                a_index,
                e_index,
            ),
        )
    )

    assert delta_result.total_cost == pytest.approx(
        full_result.total_cost
    )

    assert (
        delta_result.evaluated_weight
        == pytest.approx(
            full_result.evaluated_weight
        )
    )

    assert (
        delta_result.skipped_weight
        == pytest.approx(
            full_result.skipped_weight
        )
    )


def test_prepared_position_indexed_delta_without_changes_matches_baseline() -> None:
    (
        evaluator,
        _statistics,
        cost_matrix,
        base_positions,
        _prepared,
        baseline,
    ) = _prepare_prepared_delta_test_data()

    result = (
        evaluator
        .evaluate_prepared_position_indexed_delta(
            base_positions,
            cost_matrix,
            baseline,
            (),
        )
    )

    assert result.total_cost == pytest.approx(
        baseline.total_cost
    )

    assert (
        result.evaluated_weight
        == pytest.approx(
            baseline.evaluated_weight
        )
    )

    assert (
        result.skipped_weight
        == pytest.approx(
            baseline.skipped_weight
        )
    )


def test_prepared_position_indexed_delta_handles_missing_layout_letter() -> None:
    (
        evaluator,
        _statistics,
        cost_matrix,
        base_positions,
        prepared,
        baseline,
    ) = _prepare_prepared_delta_test_data()

    candidate_positions = list(
        base_positions
    )

    a_index = ord("A") - ord("A")

    candidate_positions[
        a_index
    ] = -1

    full_result = (
        evaluator.evaluate_prepared_position_indexed(
            candidate_positions,
            cost_matrix,
            prepared,
        )
    )

    delta_result = (
        evaluator
        .evaluate_prepared_position_indexed_delta(
            candidate_positions,
            cost_matrix,
            baseline,
            (
                a_index,
            ),
        )
    )

    assert delta_result.total_cost == pytest.approx(
        full_result.total_cost
    )

    assert (
        delta_result.evaluated_weight
        == pytest.approx(
            full_result.evaluated_weight
        )
    )

    assert (
        delta_result.skipped_weight
        == pytest.approx(
            full_result.skipped_weight
        )
    )


def test_prepared_position_indexed_delta_preserves_permanent_skips() -> None:
    layout = make_layout()
    statistics = make_statistics()

    statistics.add(
        {
            ("?", "A"): 9,
            ("A", "?"): 11,
        }
    )

    evaluator = FastLayoutScoreEvaluator(
        make_weights()
    )

    string_positions: list[str | None] = [
        None
    ] * 26

    for letter, position in layout.mapping.items():
        index = (
            ord(letter.upper())
            - ord("A")
        )

        if 0 <= index < 26:
            string_positions[index] = position

    logical_positions = tuple(
        position
        for position in string_positions
        if position is not None
    )

    (
        position_indexes,
        cost_matrix,
    ) = evaluator.build_position_index(
        logical_positions
    )

    base_positions = list(
        evaluator.convert_to_position_indexes(
            string_positions,
            position_indexes,
        )
    )

    prepared = (
        evaluator.prepare_position_indexed_transitions(
            statistics
        )
    )

    baseline = (
        evaluator
        .prepare_prepared_position_indexed_delta(
            base_positions,
            cost_matrix,
            prepared,
        )
    )

    candidate_positions = list(
        base_positions
    )

    a_index = ord("A") - ord("A")
    e_index = ord("E") - ord("A")

    (
        candidate_positions[a_index],
        candidate_positions[e_index],
    ) = (
        candidate_positions[e_index],
        candidate_positions[a_index],
    )

    full_result = (
        evaluator.evaluate_prepared_position_indexed(
            candidate_positions,
            cost_matrix,
            prepared,
        )
    )

    delta_result = (
        evaluator
        .evaluate_prepared_position_indexed_delta(
            candidate_positions,
            cost_matrix,
            baseline,
            (
                a_index,
                e_index,
            ),
        )
    )

    assert delta_result.total_cost == pytest.approx(
        full_result.total_cost
    )

    assert (
        delta_result.evaluated_weight
        == pytest.approx(
            full_result.evaluated_weight
        )
    )

    assert (
        delta_result.skipped_weight
        == pytest.approx(
            full_result.skipped_weight
        )
    )


def test_prepared_position_indexed_delta_matches_multiple_changes() -> None:
    (
        evaluator,
        _statistics,
        cost_matrix,
        base_positions,
        prepared,
        baseline,
    ) = _prepare_prepared_delta_test_data()

    candidate_positions = list(
        base_positions
    )

    indexes = tuple(
        ord(letter) - ord("A")
        for letter in (
            "A",
            "E",
            "I",
            "O",
        )
    )

    (
        a_index,
        e_index,
        i_index,
        o_index,
    ) = indexes

    (
        candidate_positions[a_index],
        candidate_positions[e_index],
    ) = (
        candidate_positions[e_index],
        candidate_positions[a_index],
    )

    (
        candidate_positions[i_index],
        candidate_positions[o_index],
    ) = (
        candidate_positions[o_index],
        candidate_positions[i_index],
    )

    full_result = (
        evaluator.evaluate_prepared_position_indexed(
            candidate_positions,
            cost_matrix,
            prepared,
        )
    )

    delta_result = (
        evaluator
        .evaluate_prepared_position_indexed_delta(
            candidate_positions,
            cost_matrix,
            baseline,
            indexes,
        )
    )

    assert delta_result.total_cost == pytest.approx(
        full_result.total_cost
    )

    assert (
        delta_result.evaluated_weight
        == pytest.approx(
            full_result.evaluated_weight
        )
    )

    assert (
        delta_result.skipped_weight
        == pytest.approx(
            full_result.skipped_weight
        )
    )


def test_prepared_position_indexed_delta_reuses_affected_index_cache() -> None:
    (
        evaluator,
        _statistics,
        cost_matrix,
        base_positions,
        _prepared,
        baseline,
    ) = _prepare_prepared_delta_test_data()

    candidate_positions = list(
        base_positions
    )

    a_index = ord("A") - ord("A")
    e_index = ord("E") - ord("A")

    (
        candidate_positions[a_index],
        candidate_positions[e_index],
    ) = (
        candidate_positions[e_index],
        candidate_positions[a_index],
    )

    evaluator.evaluate_prepared_position_indexed_delta(
        candidate_positions,
        cost_matrix,
        baseline,
        (
            a_index,
            e_index,
        ),
    )

    cache_size_after_first = len(
        baseline.affected_indexes_cache
    )

    evaluator.evaluate_prepared_position_indexed_delta(
        candidate_positions,
        cost_matrix,
        baseline,
        (
            e_index,
            a_index,
        ),
    )

    cache_size_after_second = len(
        baseline.affected_indexes_cache
    )

    assert cache_size_after_first == 1
    assert cache_size_after_second == 1


def test_prepared_position_indexed_delta_rejects_invalid_changed_index() -> None:
    (
        evaluator,
        _statistics,
        cost_matrix,
        base_positions,
        _prepared,
        baseline,
    ) = _prepare_prepared_delta_test_data()

    with pytest.raises(
        ValueError,
        match="between 0 and 25",
    ):
        evaluator.evaluate_prepared_position_indexed_delta(
            base_positions,
            cost_matrix,
            baseline,
            (
                26,
            ),
        )

