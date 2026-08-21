# tests/test_constraint_set.py

from evaluator.constraint_set import ConstraintSet
from models.constraint_evaluation import ConstraintEvaluation
from models.constraint_violation import ConstraintViolation
from models.layout import Layout


def make_layout() -> Layout:
    return Layout(
        name="Test Layout",
        version="0.1.0",
        layer="L0",
        description="Constraint set test layout",
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


class AlwaysValidConstraint:
    def evaluate(
        self,
        layout: Layout,
    ) -> ConstraintEvaluation:
        return ConstraintEvaluation(
            violations=()
        )


class FirstInvalidConstraint:
    def evaluate(
        self,
        layout: Layout,
    ) -> ConstraintEvaluation:
        return ConstraintEvaluation(
            violations=(
                ConstraintViolation(
                    constraint="first",
                    message="First violation.",
                    letter="A",
                    position=layout.position("A"),
                ),
            )
        )


class SecondInvalidConstraint:
    def evaluate(
        self,
        layout: Layout,
    ) -> ConstraintEvaluation:
        return ConstraintEvaluation(
            violations=(
                ConstraintViolation(
                    constraint="second",
                    message="Second violation.",
                    letter="B",
                    position=layout.position("B"),
                ),
            )
        )


def test_returns_constraint_evaluation():
    constraint_set = ConstraintSet(
        [AlwaysValidConstraint()]
    )

    result = constraint_set.evaluate(make_layout())

    assert isinstance(result, ConstraintEvaluation)


def test_empty_constraint_set_is_valid():
    constraint_set = ConstraintSet([])

    result = constraint_set.evaluate(make_layout())

    assert result.is_valid is True
    assert result.violation_count == 0
    assert result.violations == ()


def test_all_valid_constraints_are_valid():
    constraint_set = ConstraintSet(
        [
            AlwaysValidConstraint(),
            AlwaysValidConstraint(),
        ]
    )

    result = constraint_set.evaluate(make_layout())

    assert result.is_valid is True
    assert result.violation_count == 0


def test_single_violation_is_collected():
    constraint_set = ConstraintSet(
        [FirstInvalidConstraint()]
    )

    result = constraint_set.evaluate(make_layout())

    assert result.is_valid is False
    assert result.violation_count == 1
    assert result.violations[0].constraint == "first"


def test_multiple_violations_are_combined():
    constraint_set = ConstraintSet(
        [
            FirstInvalidConstraint(),
            SecondInvalidConstraint(),
        ]
    )

    result = constraint_set.evaluate(make_layout())

    assert result.is_valid is False
    assert result.violation_count == 2

    assert {
        violation.constraint
        for violation in result.violations
    } == {"first", "second"}


def test_constraints_are_exposed():
    constraints = (
        AlwaysValidConstraint(),
        FirstInvalidConstraint(),
    )

    constraint_set = ConstraintSet(constraints)

    assert constraint_set.constraints == constraints


def test_constraint_order_is_preserved():
    constraint_set = ConstraintSet(
        [
            FirstInvalidConstraint(),
            SecondInvalidConstraint(),
        ]
    )

    result = constraint_set.evaluate(make_layout())

    assert result.violations[0].constraint == "first"
    assert result.violations[1].constraint == "second"