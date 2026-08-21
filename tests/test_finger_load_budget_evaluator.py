# tests/test_finger_load_budget_evaluator.py

import pytest

from evaluator.finger_load_budget_evaluator import (
    FingerLoadBudgetEvaluator,
)
from models.enums import Finger, Hand
from models.finger_load import FingerLoad
from models.finger_load_budget import FingerLoadBudget


def test_actual_ratio():
    loads = (
        FingerLoad(
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            raw_count=60,
            weighted_count=60.0,
        ),
        FingerLoad(
            hand=Hand.LEFT,
            finger=Finger.MIDDLE,
            raw_count=40,
            weighted_count=40.0,
        ),
    )

    budgets = (
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            target_ratio=0.5,
        ),
    )

    evaluator = FingerLoadBudgetEvaluator()

    results = evaluator.evaluate(loads, budgets)

    assert results[0].actual_ratio == pytest.approx(0.6)


def test_no_penalty_within_budget():
    loads = (
        FingerLoad(
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            raw_count=50,
            weighted_count=50.0,
        ),
        FingerLoad(
            hand=Hand.LEFT,
            finger=Finger.MIDDLE,
            raw_count=50,
            weighted_count=50.0,
        ),
    )

    budgets = (
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            target_ratio=0.5,
        ),
    )

    evaluator = FingerLoadBudgetEvaluator()

    result = evaluator.evaluate(loads, budgets)[0]

    assert result.excess_ratio == 0.0
    assert result.penalty == 0.0


def test_penalty_above_budget():
    loads = (
        FingerLoad(
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            raw_count=70,
            weighted_count=70.0,
        ),
        FingerLoad(
            hand=Hand.LEFT,
            finger=Finger.MIDDLE,
            raw_count=30,
            weighted_count=30.0,
        ),
    )

    budgets = (
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            target_ratio=0.5,
        ),
    )

    evaluator = FingerLoadBudgetEvaluator()

    result = evaluator.evaluate(loads, budgets)[0]

    assert result.actual_ratio == pytest.approx(0.7)
    assert result.excess_ratio == pytest.approx(0.2)
    assert result.penalty == pytest.approx(0.2)


def test_tolerance_prevents_penalty():
    loads = (
        FingerLoad(
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            raw_count=55,
            weighted_count=55.0,
        ),
        FingerLoad(
            hand=Hand.LEFT,
            finger=Finger.MIDDLE,
            raw_count=45,
            weighted_count=45.0,
        ),
    )

    budgets = (
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            target_ratio=0.5,
            tolerance=0.1,
        ),
    )

    evaluator = FingerLoadBudgetEvaluator()

    result = evaluator.evaluate(loads, budgets)[0]

    assert result.penalty == 0.0


def test_tolerance_only_penalizes_excess():
    loads = (
        FingerLoad(
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            raw_count=70,
            weighted_count=70.0,
        ),
        FingerLoad(
            hand=Hand.LEFT,
            finger=Finger.MIDDLE,
            raw_count=30,
            weighted_count=30.0,
        ),
    )

    budgets = (
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            target_ratio=0.5,
            tolerance=0.1,
        ),
    )

    evaluator = FingerLoadBudgetEvaluator()

    result = evaluator.evaluate(loads, budgets)[0]

    assert result.excess_ratio == pytest.approx(0.1)
    assert result.penalty == pytest.approx(0.1)


def test_missing_finger_has_zero_load():
    loads = (
        FingerLoad(
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            raw_count=100,
            weighted_count=100.0,
        ),
    )

    budgets = (
        FingerLoadBudget(
            hand=Hand.RIGHT,
            finger=Finger.PINKY,
            target_ratio=0.1,
        ),
    )

    evaluator = FingerLoadBudgetEvaluator()

    result = evaluator.evaluate(loads, budgets)[0]

    assert result.actual_ratio == 0.0
    assert result.penalty == 0.0


def test_empty_loads():
    budgets = (
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            target_ratio=0.25,
        ),
    )

    evaluator = FingerLoadBudgetEvaluator()

    result = evaluator.evaluate((), budgets)[0]

    assert result.actual_ratio == 0.0
    assert result.excess_ratio == 0.0
    assert result.penalty == 0.0


def test_budget_rejects_invalid_target_ratio():
    with pytest.raises(ValueError):
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            target_ratio=1.1,
        )


def test_budget_rejects_invalid_tolerance():
    with pytest.raises(ValueError):
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            target_ratio=0.5,
            tolerance=-0.1,
        )