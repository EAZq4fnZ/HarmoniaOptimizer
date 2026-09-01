from __future__ import annotations

from config.harmonia_position_costs import (
    HARMONIA_POSITION_COSTS,
    make_harmonia_position_cost_profile,
)

EXPECTED_HARMONIA_POSITIONS = frozenset(
    {
        "L-P-H-0",
        "L-R-T-1",
        "L-R-H-1",
        "L-R-B-1",
        "L-M-T-2",
        "L-M-H-2",
        "L-M-B-2",
        "L-I-T-3",
        "L-I-H-3",
        "L-I-B-3",
        "L-I-T-4",
        "L-I-H-4",
        "L-I-B-4",
        "R-P-H-0",
        "R-R-T-1",
        "R-R-H-1",
        "R-R-B-1",
        "R-M-T-2",
        "R-M-H-2",
        "R-M-B-2",
        "R-I-T-3",
        "R-I-H-3",
        "R-I-B-3",
        "R-I-T-4",
        "R-I-H-4",
        "R-I-B-4",
    }
)


def test_harmonia_profile_contains_exactly_26_positions() -> None:
    assert len(HARMONIA_POSITION_COSTS) == 26
    assert (
        frozenset(HARMONIA_POSITION_COSTS)
        == EXPECTED_HARMONIA_POSITIONS
    )


def test_harmonia_position_costs_are_non_negative() -> None:
    assert all(
        cost >= 0.0
        for cost in HARMONIA_POSITION_COSTS.values()
    )


def test_left_and_right_position_costs_are_symmetric() -> None:
    for position_id, left_cost in HARMONIA_POSITION_COSTS.items():
        if not position_id.startswith("L-"):
            continue

        right_position_id = "R-" + position_id[2:]

        assert right_position_id in HARMONIA_POSITION_COSTS
        assert (
            HARMONIA_POSITION_COSTS[right_position_id]
            == left_cost
        )


def test_normal_home_is_cheaper_than_top_and_bottom() -> None:
    for hand in ("L", "R"):
        for finger, column in (
            ("R", 1),
            ("M", 2),
            ("I", 3),
        ):
            home = HARMONIA_POSITION_COSTS[
                f"{hand}-{finger}-H-{column}"
            ]
            top = HARMONIA_POSITION_COSTS[
                f"{hand}-{finger}-T-{column}"
            ]
            bottom = HARMONIA_POSITION_COSTS[
                f"{hand}-{finger}-B-{column}"
            ]

            assert home < top
            assert home < bottom


def test_index_inner_column_has_extra_reach_cost() -> None:
    for hand in ("L", "R"):
        assert (
            HARMONIA_POSITION_COSTS[f"{hand}-I-H-3"]
            < HARMONIA_POSITION_COSTS[f"{hand}-I-H-4"]
        )

        assert (
            HARMONIA_POSITION_COSTS[f"{hand}-I-T-3"]
            < HARMONIA_POSITION_COSTS[f"{hand}-I-T-4"]
        )

        assert (
            HARMONIA_POSITION_COSTS[f"{hand}-I-B-3"]
            < HARMONIA_POSITION_COSTS[f"{hand}-I-B-4"]
        )


def test_bottom_is_slightly_costlier_than_top() -> None:
    for hand in ("L", "R"):
        for finger, column in (
            ("R", 1),
            ("M", 2),
            ("I", 3),
            ("I", 4),
        ):
            assert (
                HARMONIA_POSITION_COSTS[
                    f"{hand}-{finger}-T-{column}"
                ]
                < HARMONIA_POSITION_COSTS[
                    f"{hand}-{finger}-B-{column}"
                ]
            )


def test_factory_returns_complete_profile() -> None:
    profile = make_harmonia_position_cost_profile()

    for position_id, expected_cost in (
        HARMONIA_POSITION_COSTS.items()
    ):
        assert profile.cost(position_id) == expected_cost


def test_higher_frequency_character_prefers_lower_cost_position() -> None:
    import pytest

    from evaluator.candidate_scorer import CandidateScorer
    from evaluator.character_statistics import CharacterStatistics
    from evaluator.key_position_evaluator import KeyPositionEvaluator
    from models.candidate_score import CandidateScoreWeights
    from models.layout import Layout
    from models.layout_evaluation import LayoutEvaluation

    profile = make_harmonia_position_cost_profile()
    evaluator = KeyPositionEvaluator(profile)

    statistics = CharacterStatistics()
    statistics.add(
        {
            "A": 70,
            "B": 30,
        }
    )

    remaining_mapping = {
        "C": "L-P-H-0",
        "D": "L-R-T-1",
        "E": "L-R-H-1",
        "F": "L-R-B-1",
        "G": "L-M-T-2",
        "H": "L-M-H-2",
        "I": "L-M-B-2",
        "J": "L-I-T-3",
        "K": "L-I-B-3",
        "L": "L-I-T-4",
        "M": "L-I-H-4",
        "N": "R-P-H-0",
        "O": "R-R-T-1",
        "P": "R-R-H-1",
        "Q": "R-R-B-1",
        "R": "R-M-T-2",
        "S": "R-M-H-2",
        "T": "R-M-B-2",
        "U": "R-I-T-3",
        "V": "R-I-H-3",
        "W": "R-I-B-3",
        "X": "R-I-T-4",
        "Y": "R-I-H-4",
        "Z": "R-I-B-4",
    }

    good_mapping = {
        "A": "L-I-H-3",
        "B": "L-I-B-4",
        **remaining_mapping,
    }

    bad_mapping = {
        "A": "L-I-B-4",
        "B": "L-I-H-3",
        **remaining_mapping,
    }

    good_layout = Layout(
        name="good",
        version="1.0",
        layer="L0",
        description=(
            "high-frequency character on lower-cost position"
        ),
        mapping=good_mapping,
    )

    bad_layout = Layout(
        name="bad",
        version="1.0",
        layer="L0",
        description=(
            "high-frequency character on higher-cost position"
        ),
        mapping=bad_mapping,
    )

    good_position = evaluator.evaluate(
        layout=good_layout,
        statistics=statistics,
    )
    bad_position = evaluator.evaluate(
        layout=bad_layout,
        statistics=statistics,
    )

    assert good_position.score == pytest.approx(
        0.105
    )
    assert bad_position.score == pytest.approx(
        0.245
    )
    assert (
        good_position.score
        < bad_position.score
    )

    scorer = CandidateScorer(
        CandidateScoreWeights(
            transition_weight=0.0,
            trigram_weight=0.0,
            finger_load_weight=0.0,
            position_weight=1.0,
        )
    )

    neutral_layout_evaluation = LayoutEvaluation(
        total_cost=0.0,
        evaluated_weight=1.0,
        skipped_weight=0.0,
        transitions=(),
    )

    good_score = scorer.score(
        layout_evaluation=neutral_layout_evaluation,
        finger_load_evaluations=(),
        key_position_evaluation=good_position,
    )
    bad_score = scorer.score(
        layout_evaluation=neutral_layout_evaluation,
        finger_load_evaluations=(),
        key_position_evaluation=bad_position,
    )

    assert good_score.position_score == pytest.approx(
        0.105
    )
    assert bad_score.position_score == pytest.approx(
        0.245
    )
    assert (
        good_score.total
        < bad_score.total
    )
