# tests/test_vowel_hand_distribution_constraint.py

import pytest

from evaluator.vowel_hand_distribution_constraint import (
    VowelHandDistributionConstraint,
)
from models.constraint_evaluation import ConstraintEvaluation
from models.layout import Layout


LEFT_POSITIONS = (
    "L-P-T-0",
    "L-R-T-1",
    "L-M-T-2",
    "L-I-T-3",
    "L-I-T-4",
    "L-P-H-0",
    "L-R-H-1",
    "L-M-H-2",
    "L-I-H-3",
    "L-I-H-4",
    "L-P-B-0",
    "L-R-B-1",
    "L-M-B-2",
)

RIGHT_POSITIONS = (
    "R-P-T-0",
    "R-R-T-1",
    "R-M-T-2",
    "R-I-T-3",
    "R-I-T-4",
    "R-P-H-0",
    "R-R-H-1",
    "R-M-H-2",
    "R-I-H-3",
    "R-I-H-4",
    "R-P-B-0",
    "R-R-B-1",
    "R-M-B-2",
)


def make_layout(
    left_vowels: str,
) -> Layout:
    """
    Build a valid 26-letter layout.

    Vowels listed in left_vowels are assigned to left-hand
    positions. All other vowels are assigned to right-hand
    positions.

    Remaining consonants fill the unused positions.
    """

    vowels = "AEIOU"

    if any(
        vowel not in vowels
        for vowel in left_vowels
    ):
        raise ValueError(
            "left_vowels must contain only A/E/I/O/U"
        )

    if len(set(left_vowels)) != len(left_vowels):
        raise ValueError(
            "left_vowels must not contain duplicates"
        )

    left_vowel_set = set(
        left_vowels
    )

    left_vowel_list = [
        vowel
        for vowel in vowels
        if vowel in left_vowel_set
    ]

    right_vowel_list = [
        vowel
        for vowel in vowels
        if vowel not in left_vowel_set
    ]

    mapping: dict[str, str] = {}

    for vowel, position in zip(
        left_vowel_list,
        LEFT_POSITIONS,
        strict=False,
    ):
        mapping[vowel] = position

    for vowel, position in zip(
        right_vowel_list,
        RIGHT_POSITIONS,
        strict=False,
    ):
        mapping[vowel] = position

    used_positions = set(
        mapping.values()
    )

    available_positions = [
        position
        for position in (
            LEFT_POSITIONS
            + RIGHT_POSITIONS
        )
        if position not in used_positions
    ]

    consonants = [
        letter
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if letter not in vowels
    ]

    for letter, position in zip(
        consonants,
        available_positions,
        strict=True,
    ):
        mapping[letter] = position

    return Layout(
        name="Vowel Hand Distribution Test",
        version="1.0",
        layer="L0",
        description=(
            "Vowel hand distribution constraint test"
        ),
        mapping=mapping,
    )


def make_constraint() -> VowelHandDistributionConstraint:
    return VowelHandDistributionConstraint(
        min_left_vowels=2,
        max_left_vowels=3,
    )


def test_returns_constraint_evaluation():
    layout = make_layout(
        left_vowels="AE"
    )

    result = make_constraint().evaluate(
        layout
    )

    assert isinstance(
        result,
        ConstraintEvaluation,
    )


def test_two_left_three_right_is_valid():
    layout = make_layout(
        left_vowels="AE"
    )

    result = make_constraint().evaluate(
        layout
    )

    assert result.is_valid is True


def test_three_left_two_right_is_valid():
    layout = make_layout(
        left_vowels="AEI"
    )

    result = make_constraint().evaluate(
        layout
    )

    assert result.is_valid is True


def test_one_left_four_right_is_invalid():
    layout = make_layout(
        left_vowels="A"
    )

    result = make_constraint().evaluate(
        layout
    )

    assert result.is_valid is False
    assert result.violation_count == 1


def test_four_left_one_right_is_invalid():
    layout = make_layout(
        left_vowels="AEIO"
    )

    result = make_constraint().evaluate(
        layout
    )

    assert result.is_valid is False
    assert result.violation_count == 1


def test_all_left_is_invalid():
    layout = make_layout(
        left_vowels="AEIOU"
    )

    result = make_constraint().evaluate(
        layout
    )

    assert result.is_valid is False


def test_all_right_is_invalid():
    layout = make_layout(
        left_vowels=""
    )

    result = make_constraint().evaluate(
        layout
    )

    assert result.is_valid is False


def test_violation_contains_distribution():
    layout = make_layout(
        left_vowels="A"
    )

    result = make_constraint().evaluate(
        layout
    )

    message = result.violations[0].message

    assert "left=1" in message
    assert "right=4" in message


def test_limits_are_exposed():
    constraint = make_constraint()

    assert (
        constraint.min_left_vowels
        == 2
    )

    assert (
        constraint.max_left_vowels
        == 3
    )


def test_negative_minimum_is_rejected():
    with pytest.raises(
        ValueError,
        match="min_left_vowels",
    ):
        VowelHandDistributionConstraint(
            min_left_vowels=-1,
            max_left_vowels=3,
        )


def test_maximum_above_five_is_rejected():
    with pytest.raises(
        ValueError,
        match="max_left_vowels",
    ):
        VowelHandDistributionConstraint(
            min_left_vowels=2,
            max_left_vowels=6,
        )


def test_minimum_above_maximum_is_rejected():
    with pytest.raises(
        ValueError,
        match="must not exceed",
    ):
        VowelHandDistributionConstraint(
            min_left_vowels=4,
            max_left_vowels=2,
        )