# tests/test_vowel_position_constraint.py

from evaluator.vowel_position_constraint import VowelPositionConstraint
from models.constraint_evaluation import ConstraintEvaluation
from models.layout import Layout


def make_layout() -> Layout:
    return Layout(
        name="Test Layout",
        version="0.1.0",
        layer="L0",
        description="Vowel constraint test layout",
        mapping={
            "A": "L-I-T-3",
            "B": "L-P-T-0",
            "C": "L-R-T-1",
            "D": "L-M-T-2",
            "E": "L-M-H-2",
            "F": "L-I-H-3",
            "G": "L-I-T-4",
            "H": "L-I-H-4",
            "I": "R-I-T-3",
            "J": "R-I-H-3",
            "K": "R-I-T-4",
            "L": "R-I-H-4",
            "M": "R-R-T-1",
            "N": "R-M-T-2",
            "O": "R-M-H-2",
            "P": "R-P-T-0",
            "Q": "L-P-H-0",
            "R": "L-R-H-1",
            "S": "L-M-B-2",
            "T": "L-I-B-3",
            "U": "R-R-H-1",
            "V": "R-I-B-3",
            "W": "R-M-B-2",
            "X": "R-P-H-0",
            "Y": "L-P-B-0",
            "Z": "R-P-B-0",
        },
    )


def allowed_vowel_positions() -> frozenset[str]:
    return frozenset({
        "L-I-T-3",
        "L-M-H-2",
        "R-I-T-3",
        "R-M-H-2",
        "R-R-H-1",
    })


def test_returns_constraint_evaluation():
    constraint = VowelPositionConstraint(
        allowed_vowel_positions()
    )

    result = constraint.evaluate(make_layout())

    assert isinstance(result, ConstraintEvaluation)


def test_valid_vowel_positions_are_accepted():
    constraint = VowelPositionConstraint(
        allowed_vowel_positions()
    )

    result = constraint.evaluate(make_layout())

    assert result.is_valid is True
    assert result.violation_count == 0
    assert result.violations == ()


def test_detects_disallowed_vowel_position():
    allowed = allowed_vowel_positions() - {
        "L-I-T-3"
    }

    constraint = VowelPositionConstraint(allowed)

    result = constraint.evaluate(make_layout())

    assert result.is_valid is False
    assert result.violation_count == 1

    violation = result.violations[0]

    assert violation.constraint == "vowel_position"
    assert violation.letter == "A"
    assert violation.position == "L-I-T-3"


def test_detects_multiple_disallowed_vowels():
    constraint = VowelPositionConstraint(
        frozenset({
            "L-M-H-2",
            "R-M-H-2",
        })
    )

    result = constraint.evaluate(make_layout())

    assert result.is_valid is False
    assert result.violation_count == 3

    letters = {
        violation.letter
        for violation in result.violations
    }

    assert letters == {"A", "I", "U"}


def test_consonants_do_not_need_allowed_positions():
    constraint = VowelPositionConstraint(
        allowed_vowel_positions()
    )

    result = constraint.evaluate(make_layout())

    assert result.is_valid is True


def test_violation_contains_message():
    allowed = allowed_vowel_positions() - {
        "R-R-H-1"
    }

    constraint = VowelPositionConstraint(allowed)

    result = constraint.evaluate(make_layout())

    violation = result.violations[0]

    assert "U" in violation.message
    assert "R-R-H-1" in violation.message


def test_allowed_positions_are_exposed():
    positions = allowed_vowel_positions()

    constraint = VowelPositionConstraint(positions)

    assert constraint.allowed_positions == positions