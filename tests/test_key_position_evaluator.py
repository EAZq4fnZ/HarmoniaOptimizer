from __future__ import annotations

import pytest

from evaluator.character_statistics import CharacterStatistics
from evaluator.fast_key_position_score_evaluator import (
    FastKeyPositionScoreEvaluator,
)
from evaluator.key_position_evaluator import (
    KeyPositionEvaluator,
)
from models.key_position_cost import (
    KeyPositionCostProfile,
)
from models.layout import Layout


def make_mapping() -> dict[str, str]:
    return {
        "A": "L-I-H-3",
        "B": "L-M-T-2",
        "C": "R-I-B-3",
        "D": "L-P-H-1",
        "E": "R-I-H-3",
        "F": "R-M-H-2",
        "G": "R-R-H-1",
        "H": "R-P-H-1",
        "I": "L-I-T-3",
        "J": "L-M-H-2",
        "K": "L-R-H-1",
        "L": "L-P-T-1",
        "M": "R-I-T-3",
        "N": "R-M-T-2",
        "O": "R-R-T-1",
        "P": "R-P-T-1",
        "Q": "L-I-B-3",
        "R": "L-M-B-2",
        "S": "L-R-B-1",
        "T": "L-P-B-1",
        "U": "R-I-B-4",
        "V": "R-M-B-2",
        "W": "R-R-B-1",
        "X": "R-P-B-1",
        "Y": "L-I-H-4",
        "Z": "R-I-H-4",
    }


def make_layout() -> Layout:
    return Layout(
        name="test",
        description="Key-position evaluator test layout",
        version="1.0",
        layer="L0",
        mapping=make_mapping(),
    )


def make_profile() -> KeyPositionCostProfile:
    return KeyPositionCostProfile(
        costs={
            "L-I-H-3": 0.0,
            "L-M-T-2": 1.0,
            "R-I-B-3": 2.0,
        }
    )


def make_complete_profile() -> KeyPositionCostProfile:
    return KeyPositionCostProfile(
        costs={
            position_id: float(index)
            for index, position_id in enumerate(
                make_mapping().values()
            )
        }
    )


def make_statistics(
    counts: dict[str, int],
) -> CharacterStatistics:
    statistics = CharacterStatistics()
    statistics.add(counts)
    return statistics


def test_normal_evaluator_calculates_weighted_score() -> None:
    evaluation = KeyPositionEvaluator(
        make_profile()
    ).evaluate(
        make_layout(),
        make_statistics(
            {
                "A": 10,
                "B": 20,
                "C": 30,
            }
        ),
    )

    assert evaluation.total_cost == pytest.approx(
        80.0
    )
    assert evaluation.evaluated_weight == pytest.approx(
        60.0
    )
    assert evaluation.skipped_weight == pytest.approx(
        0.0
    )
    assert evaluation.score == pytest.approx(
        80.0 / 60.0
    )


def test_normal_evaluator_skips_unmapped_character() -> None:
    evaluation = KeyPositionEvaluator(
        make_profile()
    ).evaluate(
        make_layout(),
        make_statistics(
            {
                "A": 10,
                "?": 30,
            }
        ),
    )

    assert evaluation.total_cost == pytest.approx(
        0.0
    )
    assert evaluation.evaluated_weight == pytest.approx(
        10.0
    )
    assert evaluation.skipped_weight == pytest.approx(
        30.0
    )
    assert evaluation.score == pytest.approx(
        0.0
    )


def test_normal_evaluator_skips_missing_profile_position() -> None:
    profile = KeyPositionCostProfile(
        costs={
            "L-I-H-3": 0.5,
        }
    )

    evaluation = KeyPositionEvaluator(
        profile
    ).evaluate(
        make_layout(),
        make_statistics(
            {
                "A": 10,
                "B": 20,
            }
        ),
    )

    assert evaluation.total_cost == pytest.approx(
        5.0
    )
    assert evaluation.evaluated_weight == pytest.approx(
        10.0
    )
    assert evaluation.skipped_weight == pytest.approx(
        20.0
    )
    assert evaluation.score == pytest.approx(
        0.5
    )


def test_zero_evaluated_weight_returns_zero_score() -> None:
    evaluation = KeyPositionEvaluator(
        make_profile()
    ).evaluate(
        make_layout(),
        make_statistics(
            {
                "?": 10,
            }
        ),
    )

    assert evaluation.evaluated_weight == pytest.approx(
        0.0
    )
    assert evaluation.skipped_weight == pytest.approx(
        10.0
    )
    assert evaluation.score == pytest.approx(
        0.0
    )


def test_profile_rejects_negative_cost() -> None:
    with pytest.raises(
        ValueError,
        match="non-negative",
    ):
        KeyPositionCostProfile(
            costs={
                "L-I-H-3": -0.1,
            }
        )


def test_profile_normalizes_position_id_case() -> None:
    profile = KeyPositionCostProfile(
        costs={
            " l-i-h-3 ": 0.25,
        }
    )

    assert profile.cost(
        "L-I-H-3"
    ) == pytest.approx(
        0.25
    )


def test_fast_evaluator_matches_normal() -> None:
    layout = make_layout()
    profile = make_profile()

    statistics = make_statistics(
        {
            "A": 17,
            "B": 23,
            "C": 41,
        }
    )

    normal = KeyPositionEvaluator(
        profile
    ).evaluate(
        layout,
        statistics,
    ).score

    fast = FastKeyPositionScoreEvaluator(
        profile
    ).evaluate(
        layout,
        statistics,
    )

    assert fast == pytest.approx(
        normal
    )


def test_fast_mapping_matches_normal_with_skipped_weight() -> None:
    layout = make_layout()

    profile = KeyPositionCostProfile(
        costs={
            "L-I-H-3": 0.25,
            "L-M-T-2": 0.75,
        }
    )

    statistics = make_statistics(
        {
            "A": 10,
            "B": 20,
            "C": 30,
            "?": 40,
        }
    )

    normal = KeyPositionEvaluator(
        profile
    ).evaluate(
        layout,
        statistics,
    ).score

    fast = FastKeyPositionScoreEvaluator(
        profile
    ).evaluate_mapping(
        layout.mapping,
        statistics,
    )

    assert fast == pytest.approx(
        normal
    )


def test_fast_prepared_matches_normal() -> None:
    layout = make_layout()
    profile = make_complete_profile()

    statistics = make_statistics(
        {
            "A": 10,
            "B": 20,
            "C": 30,
            "E": 40,
            "I": 50,
            "O": 60,
            "U": 70,
            "Z": 80,
        }
    )

    evaluator = FastKeyPositionScoreEvaluator(
        profile
    )

    unique_positions = tuple(
        layout.mapping.values()
    )

    position_indexes = {
        position_id: index
        for index, position_id in enumerate(
            unique_positions
        )
    }

    positions = [
        position_indexes[
            layout.mapping[
                chr(ord("A") + index)
            ]
        ]
        for index in range(26)
    ]

    position_costs = (
        evaluator.build_position_costs(
            unique_positions
        )
    )

    (
        weighted_statistics,
        total_weighted_load,
    ) = evaluator.prepare_position_indexed_statistics(
        statistics
    )

    normal = KeyPositionEvaluator(
        profile
    ).evaluate(
        layout,
        statistics,
    ).score

    fast = (
        evaluator
        .evaluate_prepared_position_indexed_complete(
            positions,
            position_costs,
            weighted_statistics,
            total_weighted_load,
        )
    )

    assert fast == pytest.approx(
        normal
    )


def test_build_position_costs_rejects_missing_position() -> None:
    evaluator = FastKeyPositionScoreEvaluator(
        KeyPositionCostProfile(
            costs={
                "L-I-H-3": 0.0,
            }
        )
    )

    with pytest.raises(
        ValueError,
        match="missing key position cost",
    ):
        evaluator.build_position_costs(
            (
                "L-I-H-3",
                "R-I-H-3",
            )
        )
