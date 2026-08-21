# tests/test_forbidden_position_constraint.py

from evaluator.forbidden_position_constraint import (
    ForbiddenPositionConstraint,
)
from models.constraint_evaluation import ConstraintEvaluation
from models.layout import Layout


def make_layout() -> Layout:
    return Layout(
        name="Test Layout",
        version="0.1.0",
        layer="L0",
        description="Constraint test layout",
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


def test_returns_constraint_evaluation():
    constraint = ForbiddenPositionConstraint(
        frozenset()
    )

    result = constraint.evaluate(make_layout())

    assert isinstance(result, ConstraintEvaluation)


def test_layout_without_forbidden_positions_is_valid():
    constraint = ForbiddenPositionConstraint(
        frozenset()
    )

    result = constraint.evaluate(make_layout())

    assert result.is_valid is True
    assert result.violation_count == 0
    assert result.violations == ()


def test_detects_single_forbidden_position():
    constraint = ForbiddenPositionConstraint(
        frozenset({"L-P-T-0"})
    )

    result = constraint.evaluate(make_layout())

    assert result.is_valid is False
    assert result.violation_count == 1

    violation = result.violations[0]

    assert violation.constraint == "forbidden_position"
    assert violation.letter == "S"
    assert violation.position == "L-P-T-0"


def test_detects_multiple_forbidden_positions():
    constraint = ForbiddenPositionConstraint(
        frozenset({
            "L-P-T-0",
            "L-P-B-0",
            "R-P-T-0",
            "R-P-B-0",
        })
    )

    result = constraint.evaluate(make_layout())

    assert result.is_valid is False
    assert result.violation_count == 4

    letters = {
        violation.letter
        for violation in result.violations
    }

    assert letters == {"S", "T", "V", "W"}


def test_violation_contains_message():
    constraint = ForbiddenPositionConstraint(
        frozenset({"L-P-T-0"})
    )

    result = constraint.evaluate(make_layout())

    violation = result.violations[0]

    assert "S" in violation.message
    assert "L-P-T-0" in violation.message


def test_home_pinky_can_remain_allowed():
    constraint = ForbiddenPositionConstraint(
        frozenset({
            "L-P-T-0",
            "L-P-B-0",
            "R-P-T-0",
            "R-P-B-0",
        })
    )

    result = constraint.evaluate(make_layout())

    forbidden_letters = {
        violation.letter
        for violation in result.violations
    }

    assert "R" not in forbidden_letters
    assert "U" not in forbidden_letters


def test_forbidden_positions_are_exposed():
    positions = frozenset({
        "L-P-T-0",
        "R-P-T-0",
    })

    constraint = ForbiddenPositionConstraint(
        positions
    )

    assert constraint.forbidden_positions == positions