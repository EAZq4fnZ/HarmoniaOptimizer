# tests/test_trigram_layout_evaluator.py

import string

import pytest

from evaluator.trigram_layout_evaluator import (
    TrigramLayoutEvaluator,
)
from evaluator.trigram_statistics import TrigramStatistics
from models.layout import Layout
from models.trigram_cost import TrigramCostWeights


def make_layout() -> Layout:
    preferred_positions = [
        # A -> B -> C:
        # left-hand inward roll
        "L-R-H-1",
        "L-M-H-1",
        "L-I-H-1",

        # D -> E -> F:
        # left-hand redirect
        "L-R-T-1",
        "L-M-T-1",
        "L-R-T-2",

        # G -> H -> I:
        # alternating hands L-R-L
        "L-I-B-1",
        "R-I-B-1",
        "L-M-B-1",
    ]

    all_positions = []

    for hand in ("L", "R"):
        for finger in ("P", "R", "M", "I"):
            for row in ("T", "H", "B"):
                for column in (1, 2, 3, 4):
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
        name="Trigram Layout Evaluator Test",
        version="0.1.0",
        layer="L0",
        description="TrigramLayoutEvaluator test",
        mapping=mapping,
    )


def make_weights() -> TrigramCostWeights:
    return TrigramCostWeights(
        same_finger_skip_penalty=8.0,
        redirect_penalty=4.0,
        alternation_reward=2.0,
        inward_roll_reward=1.5,
        outward_roll_reward=0.5,
    )


def test_inward_roll_total_cost() -> None:
    statistics = TrigramStatistics()
    statistics.record(
        "A",
        "B",
        "C",
    )

    evaluator = TrigramLayoutEvaluator(
        make_weights()
    )

    result = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    assert result.total_cost == pytest.approx(-1.5)
    assert result.evaluated_weight == pytest.approx(1.0)
    assert result.score == pytest.approx(-1.5)


def test_applies_weighted_frequency() -> None:
    statistics = TrigramStatistics()

    statistics.record(
        "A",
        "B",
        "C",
        weight=3.0,
    )
    statistics.record(
        "A",
        "B",
        "C",
        weight=3.0,
    )

    evaluator = TrigramLayoutEvaluator(
        make_weights()
    )

    result = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    # Raw count = 2
    # Weighted count = 6
    # Inward roll cost = -1.5
    # Weighted total = -9
    assert result.total_cost == pytest.approx(-9.0)
    assert result.evaluated_weight == pytest.approx(6.0)
    assert result.score == pytest.approx(-1.5)


def test_redirect_cost() -> None:
    statistics = TrigramStatistics()

    statistics.record(
        "D",
        "E",
        "F",
    )

    evaluator = TrigramLayoutEvaluator(
        make_weights()
    )

    result = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    # D-E-F is also a same-finger skip:
    # ring -> middle -> ring
    #
    # SFS takes precedence over redirect.
    assert result.total_cost == pytest.approx(8.0)

    record = result.trigrams[0]

    assert record.cost.same_finger_skip == pytest.approx(8.0)
    assert record.cost.redirect == pytest.approx(0.0)


def test_alternation_reward() -> None:
    statistics = TrigramStatistics()

    statistics.record(
        "G",
        "H",
        "I",
    )

    evaluator = TrigramLayoutEvaluator(
        make_weights()
    )

    result = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    assert result.total_cost == pytest.approx(-2.0)
    assert result.score == pytest.approx(-2.0)


def test_combines_trigrams() -> None:
    statistics = TrigramStatistics()

    statistics.record(
        "A",
        "B",
        "C",
    )
    statistics.record(
        "G",
        "H",
        "I",
    )

    evaluator = TrigramLayoutEvaluator(
        make_weights()
    )

    result = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    # ABC = -1.5
    # GHI = -2.0
    #
    # total = -3.5
    # evaluated weight = 2
    # normalized score = -1.75
    assert result.total_cost == pytest.approx(-3.5)
    assert result.evaluated_weight == pytest.approx(2.0)
    assert result.score == pytest.approx(-1.75)


def test_contains_breakdown() -> None:
    statistics = TrigramStatistics()

    statistics.record(
        "A",
        "B",
        "C",
        weight=2.0,
    )

    evaluator = TrigramLayoutEvaluator(
        make_weights()
    )

    result = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    assert result.trigram_count == 1

    record = result.trigrams[0]

    assert record.first == "A"
    assert record.second == "B"
    assert record.third == "C"
    assert record.raw_count == 1
    assert record.weighted_count == pytest.approx(2.0)
    assert record.cost.total == pytest.approx(-1.5)
    assert record.weighted_cost == pytest.approx(-3.0)


def test_unsupported_trigram_is_skipped() -> None:
    statistics = TrigramStatistics()

    statistics.record(
        "A",
        "B",
        "C",
    )
    statistics.record(
        "A",
        "B",
        ".",
        weight=3.0,
    )

    evaluator = TrigramLayoutEvaluator(
        make_weights()
    )

    result = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    assert result.total_cost == pytest.approx(-1.5)
    assert result.evaluated_weight == pytest.approx(1.0)
    assert result.skipped_weight == pytest.approx(3.0)
    assert result.trigram_count == 1


def test_zero_evaluated_weight_has_zero_score() -> None:
    statistics = TrigramStatistics()

    statistics.record(
        "A",
        "B",
        ".",
    )

    evaluator = TrigramLayoutEvaluator(
        make_weights()
    )

    result = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    assert result.evaluated_weight == pytest.approx(0.0)
    assert result.skipped_weight == pytest.approx(1.0)
    assert result.score == pytest.approx(0.0)


def test_lowercase_statistics_are_supported() -> None:
    statistics = TrigramStatistics()

    statistics.record(
        "a",
        "b",
        "c",
    )

    evaluator = TrigramLayoutEvaluator(
        make_weights()
    )

    result = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    assert result.total_cost == pytest.approx(-1.5)
