# tests/test_layout_evaluator.py

import string

from evaluator.layout_evaluator import LayoutEvaluator
from evaluator.transition_statistics import TransitionStatistics
from models.layout import Layout
from models.transition_cost import TransitionCostWeights


def make_layout() -> Layout:
    preferred_positions = [
        # A -> B:
        # alternating hands, same row
        "L-I-H-1",
        "R-I-H-1",

        # A -> C:
        # same hand, same finger, row change
        "L-I-T-1",
    ]

    all_positions = []

    for hand in ("L", "R"):
        for finger in ("P", "R", "M", "I"):
            for row in ("T", "H", "B"):
                for column in (1, 2):
                    position = (
                        f"{hand}-{finger}-{row}-{column}"
                    )

                    if position not in preferred_positions:
                        all_positions.append(position)

    positions = (
        preferred_positions
        + all_positions
    )[:26]

    mapping = dict(
        zip(
            string.ascii_uppercase,
            positions,
            strict=True,
        )
    )

    return Layout(
        name="Layout Evaluator Test",
        version="0.1.0",
        layer="L0",
        description="LayoutEvaluator test",
        mapping=mapping,
    )


def make_weights() -> TransitionCostWeights:
    return TransitionCostWeights(
        same_finger_penalty=10.0,
        same_hand_penalty=2.0,
        row_change_penalty=1.5,
        alternation_reward=2.0,
        inward_roll_reward=1.5,
        outward_roll_reward=0.5,
    )


def test_layout_evaluator_returns_total_cost():
    statistics = TransitionStatistics()

    statistics.add(
        {
            ("A", "B"): 1,
        }
    )

    evaluator = LayoutEvaluator(
        make_weights()
    )

    result = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    # A -> B is alternating:
    # alternation reward = -2.0
    assert result.total_cost == -2.0


def test_layout_evaluator_applies_weight():
    statistics = TransitionStatistics()

    statistics.add(
        {
            ("A", "B"): 2,
        },
        weight=3.0,
    )

    evaluator = LayoutEvaluator(
        make_weights()
    )

    result = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    # Weighted frequency:
    # 2 * 3 = 6
    #
    # Transition cost:
    # -2
    #
    # Total:
    # 6 * -2 = -12
    assert result.total_cost == -12.0


def test_layout_evaluator_same_finger_cost():
    statistics = TransitionStatistics()

    statistics.add(
        {
            ("A", "C"): 1,
        }
    )

    evaluator = LayoutEvaluator(
        make_weights()
    )

    result = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    # A -> C:
    # same finger = 10
    # same hand = 2
    # row change = 1.5
    #
    # total = 13.5
    assert result.total_cost == 13.5


def test_layout_evaluator_combines_transitions():
    statistics = TransitionStatistics()

    statistics.add(
        {
            ("A", "B"): 1,
            ("A", "C"): 1,
        }
    )

    evaluator = LayoutEvaluator(
        make_weights()
    )

    result = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    # AB = -2.0
    # AC = 13.5
    #
    # total = 11.5
    assert result.total_cost == 11.5


def test_layout_evaluation_contains_breakdown():
    statistics = TransitionStatistics()

    statistics.add(
        {
            ("A", "B"): 2,
        },
        weight=3.0,
    )

    evaluator = LayoutEvaluator(
        make_weights()
    )

    result = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    assert result.transition_count == 1

    transition = result.transitions[0]

    assert transition.source == "A"
    assert transition.target == "B"
    assert transition.raw_count == 2
    assert transition.weighted_count == 6.0
    assert transition.cost.total == -2.0
    assert transition.weighted_cost == -12.0


def test_layout_evaluator_accepts_lowercase_statistics():
    statistics = TransitionStatistics()

    statistics.add(
        {
            ("a", "b"): 1,
        }
    )

    evaluator = LayoutEvaluator(
        make_weights()
    )

    result = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    assert result.total_cost == -2.0


def test_unsupported_transition_is_skipped():
    statistics = TransitionStatistics()

    statistics.add(
        {
            ("A", "B"): 1,
            ("A", " "): 3,
        }
    )

    evaluator = LayoutEvaluator(
        make_weights()
    )

    result = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    assert result.total_cost == -2.0

    assert result.evaluated_weight == 1.0
    assert result.skipped_weight == 3.0


def test_only_supported_transitions_are_recorded():
    statistics = TransitionStatistics()

    statistics.add(
        {
            ("A", "B"): 1,
            ("A", "."): 1,
        }
    )

    evaluator = LayoutEvaluator(
        make_weights()
    )

    result = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    assert result.transition_count == 1
    assert result.transitions[0].source == "A"
    assert result.transitions[0].target == "B"