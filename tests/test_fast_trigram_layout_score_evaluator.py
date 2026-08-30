# tests/test_fast_trigram_layout_score_evaluator.py

from __future__ import annotations

from itertools import product

import pytest

from evaluator.fast_trigram_layout_score_evaluator import (
    FastTrigramLayoutScoreEvaluator,
)
from evaluator.trigram_cost_evaluator import TrigramCostEvaluator
from evaluator.trigram_evaluator import TrigramEvaluator
from evaluator.trigram_layout_evaluator import TrigramLayoutEvaluator
from evaluator.trigram_statistics import TrigramStatistics
from models.enums import Finger, Hand, Layer, Row
from models.layout import Layout
from models.logical_key import LogicalKey
from models.logical_position import LogicalPosition
from models.trigram_cost import TrigramCostWeights

TEST_WEIGHTS = TrigramCostWeights(
    same_finger_skip_penalty=8.0,
    redirect_penalty=4.0,
    alternation_reward=2.0,
    inward_roll_reward=1.5,
    outward_roll_reward=0.5,
)

_HAND_CODE = {
    Hand.LEFT: "L",
    Hand.RIGHT: "R",
}

_FINGER_CODE = {
    Finger.PINKY: "P",
    Finger.RING: "R",
    Finger.MIDDLE: "M",
    Finger.INDEX: "I",
}

_ROW_CODE = {
    Row.TOP: "T",
    Row.HOME: "H",
    Row.BOTTOM: "B",
}


def _position(
    hand: Hand,
    finger: Finger,
    row: Row,
    column: int,
) -> LogicalPosition:
    return LogicalPosition(
        layer=Layer.L0,
        hand=hand,
        finger=finger,
        row=row,
        column=column,
    )


def _test_positions() -> tuple[LogicalPosition, ...]:
    """
    Return a compact structurally complete set of non-thumb positions.

    Every non-thumb finger is represented on both hands.
    """

    return (
        _position(
            Hand.LEFT,
            Finger.PINKY,
            Row.HOME,
            0,
        ),
        _position(
            Hand.LEFT,
            Finger.RING,
            Row.TOP,
            1,
        ),
        _position(
            Hand.LEFT,
            Finger.MIDDLE,
            Row.HOME,
            2,
        ),
        _position(
            Hand.LEFT,
            Finger.INDEX,
            Row.TOP,
            3,
        ),
        _position(
            Hand.RIGHT,
            Finger.INDEX,
            Row.HOME,
            0,
        ),
        _position(
            Hand.RIGHT,
            Finger.MIDDLE,
            Row.TOP,
            1,
        ),
        _position(
            Hand.RIGHT,
            Finger.RING,
            Row.HOME,
            2,
        ),
        _position(
            Hand.RIGHT,
            Finger.PINKY,
            Row.TOP,
            3,
        ),
    )


def _logical_key(
    key_id: str,
    position: LogicalPosition,
) -> LogicalKey:
    return LogicalKey(
        id=key_id,
        position=position,
    )


def _normal_cost(
    first: LogicalPosition,
    second: LogicalPosition,
    third: LogicalPosition,
) -> float:
    trigram_evaluator = TrigramEvaluator()

    cost_evaluator = TrigramCostEvaluator(
        TEST_WEIGHTS
    )

    features = trigram_evaluator.evaluate(
        _logical_key("A", first),
        _logical_key("B", second),
        _logical_key("C", third),
    )

    return cost_evaluator.evaluate(
        features
    ).total


def _position_id(
    position: LogicalPosition,
) -> str:
    """
    Convert LogicalPosition to the canonical parser format.

    Example:
        L-M-H-2
    """

    return (
        f"{_HAND_CODE[position.hand]}-"
        f"{_FINGER_CODE[position.finger]}-"
        f"{_ROW_CODE[position.row]}-"
        f"{position.column}"
    )


def _layout() -> Layout:
    """
    Build a complete A-Z layout using 26 unique logical positions.

    Current trigram structural features depend on hand/finger
    movement rather than row/column, so row and column combinations
    are used here to obtain 26 unique logical position IDs.
    """

    fingers = (
        Finger.PINKY,
        Finger.RING,
        Finger.MIDDLE,
        Finger.INDEX,
    )

    rows = (
        Row.TOP,
        Row.HOME,
        Row.BOTTOM,
    )

    positions: list[LogicalPosition] = []

    column = 0

    while len(positions) < 26:
        for hand in (
            Hand.LEFT,
            Hand.RIGHT,
        ):
            for finger in fingers:
                for row in rows:
                    positions.append(
                        _position(
                            hand,
                            finger,
                            row,
                            column,
                        )
                    )

                    if len(positions) == 26:
                        break

                if len(positions) == 26:
                    break

            if len(positions) == 26:
                break

        column += 1

    mapping = {
        chr(ord("A") + index): (
            _position_id(position)
        )
        for index, position in enumerate(
            positions
        )
    }

    return Layout(
        name="fast-trigram-test",
        version="1.0",
        layer="L0",
        description=(
            "Synthetic complete layout for "
            "fast trigram evaluator tests."
        ),
        mapping=mapping,
    )


def test_cost_cube_matches_normal_trigram_cost_for_all_position_triples() -> None:
    """
    Every structural position triple must have exactly the same
    numeric cost in the normal and fast evaluators.
    """

    positions = _test_positions()

    position_ids = tuple(
        _position_id(position)
        for position in positions
    )

    fast_evaluator = (
        FastTrigramLayoutScoreEvaluator(
            TEST_WEIGHTS
        )
    )

    cube = fast_evaluator.build_cost_cube(
        position_ids
    )

    for (
        first_index,
        second_index,
        third_index,
    ) in product(
        range(len(positions)),
        repeat=3,
    ):
        expected = _normal_cost(
            positions[first_index],
            positions[second_index],
            positions[third_index],
        )

        actual = cube[
            first_index
        ][
            second_index
        ][
            third_index
        ]

        assert actual == pytest.approx(
            expected
        )


def test_prepare_position_indexed_trigrams() -> None:
    statistics = TrigramStatistics()

    statistics.record(
        "A",
        "B",
        "C",
        weight=2.5,
    )

    statistics.record(
        "C",
        "A",
        "B",
        weight=1.5,
    )

    evaluator = (
        FastTrigramLayoutScoreEvaluator(
            TEST_WEIGHTS
        )
    )

    prepared = (
        evaluator
        .prepare_position_indexed_trigrams(
            statistics
        )
    )

    assert prepared.records == (
        (
            0,
            1,
            2,
            2.5,
        ),
        (
            2,
            0,
            1,
            1.5,
        ),
    )

    assert (
        prepared.evaluated_weight
        == pytest.approx(4.0)
    )

    assert (
        prepared.permanently_skipped_weight
        == pytest.approx(0.0)
    )


def test_fast_complete_evaluation_matches_normal_layout_evaluation() -> None:
    layout = _layout()

    statistics = TrigramStatistics()

    statistics.record(
        "A",
        "B",
        "C",
        weight=3.0,
    )

    statistics.record(
        "D",
        "E",
        "F",
        weight=2.0,
    )

    statistics.record(
        "G",
        "H",
        "I",
        weight=4.0,
    )

    statistics.record(
        "A",
        "E",
        "A",
        weight=5.0,
    )

    statistics.record(
        "J",
        "K",
        "L",
        weight=1.0,
    )

    normal_evaluator = TrigramLayoutEvaluator(
        TEST_WEIGHTS
    )

    normal = normal_evaluator.evaluate(
        layout,
        statistics,
    )

    fast_evaluator = (
        FastTrigramLayoutScoreEvaluator(
            TEST_WEIGHTS
        )
    )

    position_ids = tuple(
        layout[
            chr(ord("A") + index)
        ]
        for index in range(26)
    )

    cost_cube = fast_evaluator.build_cost_cube(
        position_ids
    )

    prepared = (
        fast_evaluator
        .prepare_position_indexed_trigrams(
            statistics
        )
    )

    position_indexes = tuple(
        range(26)
    )

    fast = (
        fast_evaluator
        .evaluate_prepared_position_indexed_complete(
            position_indexes,
            cost_cube,
            prepared,
        )
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

    assert fast.score == pytest.approx(
        normal.score
    )


def test_scalar_total_cost_matches_fast_result() -> None:
    layout = _layout()

    statistics = TrigramStatistics()

    statistics.record(
        "A",
        "B",
        "C",
        weight=3.0,
    )

    statistics.record(
        "D",
        "E",
        "F",
        weight=2.0,
    )

    statistics.record(
        "A",
        "E",
        "A",
        weight=5.0,
    )

    evaluator = (
        FastTrigramLayoutScoreEvaluator(
            TEST_WEIGHTS
        )
    )

    position_ids = tuple(
        layout[
            chr(ord("A") + index)
        ]
        for index in range(26)
    )

    cost_cube = evaluator.build_cost_cube(
        position_ids
    )

    prepared = (
        evaluator
        .prepare_position_indexed_trigrams(
            statistics
        )
    )

    position_indexes = tuple(
        range(26)
    )

    full_result = (
        evaluator
        .evaluate_prepared_position_indexed_complete(
            position_indexes,
            cost_cube,
            prepared,
        )
    )

    scalar_total = (
        evaluator
        .evaluate_prepared_position_indexed_complete_total_cost(
            position_indexes,
            cost_cube,
            prepared,
        )
    )

    assert scalar_total == pytest.approx(
        full_result.total_cost
    )


def test_zero_evaluated_weight_has_zero_score() -> None:
    evaluator = (
        FastTrigramLayoutScoreEvaluator(
            TEST_WEIGHTS
        )
    )

    statistics = TrigramStatistics()

    prepared = (
        evaluator
        .prepare_position_indexed_trigrams(
            statistics
        )
    )

    score = (
        evaluator
        .evaluate_prepared_position_indexed_complete(
            tuple(range(26)),
            (),
            prepared,
        )
    )

    assert score.total_cost == 0.0
    assert score.evaluated_weight == 0.0
    assert score.skipped_weight == 0.0
    assert score.score == 0.0


def test_complete_evaluation_rejects_wrong_position_count() -> None:
    evaluator = (
        FastTrigramLayoutScoreEvaluator(
            TEST_WEIGHTS
        )
    )

    statistics = TrigramStatistics()

    prepared = (
        evaluator
        .prepare_position_indexed_trigrams(
            statistics
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "position_indexes must contain "
            "exactly 26 entries"
        ),
    ):
        evaluator.evaluate_prepared_position_indexed_complete(
            tuple(range(25)),
            (),
            prepared,
        )


def test_scalar_evaluation_rejects_wrong_position_count() -> None:
    evaluator = (
        FastTrigramLayoutScoreEvaluator(
            TEST_WEIGHTS
        )
    )

    statistics = TrigramStatistics()

    prepared = (
        evaluator
        .prepare_position_indexed_trigrams(
            statistics
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "position_indexes must contain "
            "exactly 26 entries"
        ),
    ):
        evaluator.evaluate_prepared_position_indexed_complete_total_cost(
            tuple(range(25)),
            (),
            prepared,
        )