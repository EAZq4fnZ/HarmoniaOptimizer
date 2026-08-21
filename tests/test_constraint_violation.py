# tests/test_constraint_violation.py

from dataclasses import FrozenInstanceError

import pytest

from models.constraint_violation import ConstraintViolation


def test_constraint_violation_attributes():
    violation = ConstraintViolation(
        constraint="forbidden_position",
        message="Pinky top row is forbidden.",
        letter="Q",
        position="L-P-T-0",
    )

    assert violation.constraint == "forbidden_position"
    assert violation.message == "Pinky top row is forbidden."
    assert violation.letter == "Q"
    assert violation.position == "L-P-T-0"


def test_letter_is_optional():
    violation = ConstraintViolation(
        constraint="test",
        message="Test violation.",
    )

    assert violation.letter is None


def test_position_is_optional():
    violation = ConstraintViolation(
        constraint="test",
        message="Test violation.",
    )

    assert violation.position is None


def test_constraint_violation_is_immutable():
    violation = ConstraintViolation(
        constraint="test",
        message="Test violation.",
    )

    with pytest.raises(FrozenInstanceError):
        violation.constraint = "changed"


def test_constraint_violation_is_hashable():
    violation = ConstraintViolation(
        constraint="test",
        message="Test violation.",
    )

    values = {violation}

    assert violation in values


def test_empty_constraint_is_rejected():
    with pytest.raises(ValueError):
        ConstraintViolation(
            constraint="",
            message="Test violation.",
        )


def test_whitespace_constraint_is_rejected():
    with pytest.raises(ValueError):
        ConstraintViolation(
            constraint="   ",
            message="Test violation.",
        )


def test_empty_message_is_rejected():
    with pytest.raises(ValueError):
        ConstraintViolation(
            constraint="test",
            message="",
        )


def test_whitespace_message_is_rejected():
    with pytest.raises(ValueError):
        ConstraintViolation(
            constraint="test",
            message="   ",
        )