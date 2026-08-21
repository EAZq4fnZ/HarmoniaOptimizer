# tests/test_finger_load_pipeline.py

import pytest

from evaluator.character_statistics import CharacterStatistics
from evaluator.finger_load_pipeline import FingerLoadPipeline
from models.enums import Finger, Hand
from models.finger_load_budget import FingerLoadBudget
from models.layout import Layout


def make_layout() -> Layout:
    return Layout(
        name="Test Layout",
        version="0.1.0",
        layer="L0",
        description="Finger load pipeline test layout",
        mapping={
            "A": "L-M-H-2",
            "B": "L-M-T-2",
            "C": "L-R-H-1",
            "D": "L-R-T-1",
            "E": "L-I-H-3",
            "F": "L-I-T-3",
            "G": "L-I-H-4",
            "H": "L-I-T-4",
            "I": "L-M-B-2",
            "J": "R-I-H-4",
            "K": "R-I-T-4",
            "L": "R-I-H-3",
            "M": "R-I-T-3",
            "N": "R-M-H-2",
            "O": "R-M-T-2",
            "P": "R-R-H-1",
            "Q": "R-R-T-1",
            "R": "L-P-H-0",
            "S": "L-P-T-0",
            "T": "L-P-B-0",
            "U": "R-P-H-0",
            "V": "R-P-T-0",
            "W": "R-P-B-0",
            "X": "L-I-B-3",
            "Y": "R-I-B-3",
            "Z": "R-M-B-2",
        },
    )


def find_result(
    results,
    hand: Hand,
    finger: Finger,
):
    return next(
        result
        for result in results
        if result.hand == hand
        and result.finger == finger
    )


def test_pipeline_calculates_actual_ratio():
    statistics = CharacterStatistics()
    statistics.add(
        {
            "a": 60,
            "c": 40,
        }
    )

    budgets = (
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.MIDDLE,
            target_ratio=0.5,
        ),
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.RING,
            target_ratio=0.5,
        ),
    )

    pipeline = FingerLoadPipeline()

    results = pipeline.evaluate(
        make_layout(),
        statistics,
        budgets,
    )

    middle = find_result(
        results,
        Hand.LEFT,
        Finger.MIDDLE,
    )

    ring = find_result(
        results,
        Hand.LEFT,
        Finger.RING,
    )

    assert middle.actual_ratio == pytest.approx(0.6)
    assert ring.actual_ratio == pytest.approx(0.4)


def test_pipeline_calculates_penalty():
    statistics = CharacterStatistics()
    statistics.add(
        {
            "a": 70,
            "c": 30,
        }
    )

    budgets = (
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.MIDDLE,
            target_ratio=0.5,
        ),
    )

    pipeline = FingerLoadPipeline()

    results = pipeline.evaluate(
        make_layout(),
        statistics,
        budgets,
    )

    result = results[0]

    assert result.actual_ratio == pytest.approx(0.7)
    assert result.excess_ratio == pytest.approx(0.2)
    assert result.penalty == pytest.approx(0.2)


def test_pipeline_applies_character_weight():
    statistics = CharacterStatistics()

    statistics.add(
        {"a": 10},
        weight=3.0,
    )

    statistics.add(
        {"c": 10},
        weight=1.0,
    )

    budgets = (
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.MIDDLE,
            target_ratio=0.5,
        ),
    )

    pipeline = FingerLoadPipeline()

    results = pipeline.evaluate(
        make_layout(),
        statistics,
        budgets,
    )

    result = results[0]

    assert result.actual_ratio == pytest.approx(0.75)
    assert result.penalty == pytest.approx(0.25)


def test_pipeline_separates_left_and_right_index():
    statistics = CharacterStatistics()

    statistics.add(
        {
            "e": 75,
            "l": 25,
        }
    )

    budgets = (
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            target_ratio=0.5,
        ),
        FingerLoadBudget(
            hand=Hand.RIGHT,
            finger=Finger.INDEX,
            target_ratio=0.5,
        ),
    )

    pipeline = FingerLoadPipeline()

    results = pipeline.evaluate(
        make_layout(),
        statistics,
        budgets,
    )

    left = find_result(
        results,
        Hand.LEFT,
        Finger.INDEX,
    )

    right = find_result(
        results,
        Hand.RIGHT,
        Finger.INDEX,
    )

    assert left.actual_ratio == pytest.approx(0.75)
    assert right.actual_ratio == pytest.approx(0.25)

    assert left.penalty == pytest.approx(0.25)
    assert right.penalty == 0.0


def test_pipeline_ignores_unsupported_characters():
    statistics = CharacterStatistics()

    statistics.add(
        {
            "a": 50,
            ".": 100,
            " ": 100,
        }
    )

    budgets = (
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.MIDDLE,
            target_ratio=0.5,
        ),
    )

    pipeline = FingerLoadPipeline()

    results = pipeline.evaluate(
        make_layout(),
        statistics,
        budgets,
    )

    result = results[0]

    # Unsupported characters are excluded from the denominator.
    assert result.actual_ratio == pytest.approx(1.0)
    assert result.penalty == pytest.approx(0.5)


def test_pipeline_respects_tolerance():
    statistics = CharacterStatistics()

    statistics.add(
        {
            "a": 55,
            "c": 45,
        }
    )

    budgets = (
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.MIDDLE,
            target_ratio=0.5,
            tolerance=0.1,
        ),
    )

    pipeline = FingerLoadPipeline()

    results = pipeline.evaluate(
        make_layout(),
        statistics,
        budgets,
    )

    result = results[0]

    assert result.actual_ratio == pytest.approx(0.55)
    assert result.excess_ratio == 0.0
    assert result.penalty == 0.0