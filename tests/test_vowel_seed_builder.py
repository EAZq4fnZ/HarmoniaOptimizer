# tests/test_vowel_seed_builder.py

import pytest

from models.layout import Layout
from optimizer.vowel_seed_builder import VowelSeedBuilder


class DummyEvaluator:
    pass


def make_layout() -> Layout:
    return Layout(
        name="Vowel Seed Test",
        version="1.0",
        layer="L0",
        description="Vowel seed builder test layout",
        mapping={
            "A": "L-M-H-2",
            "B": "R-R-T-1",
            "C": "L-I-B-3",
            "D": "R-M-H-2",
            "E": "R-I-T-3",
            "F": "L-P-H-0",
            "G": "R-I-B-3",
            "H": "R-I-H-3",
            "I": "L-I-H-3",
            "J": "R-I-B-4",
            "K": "L-I-T-4",
            "L": "L-R-H-1",
            "M": "R-R-H-1",
            "N": "R-I-H-4",
            "O": "L-I-H-4",
            "P": "R-M-T-2",
            "Q": "R-R-B-1",
            "R": "L-I-T-3",
            "S": "L-I-B-4",
            "T": "L-M-T-2",
            "U": "R-I-T-4",
            "V": "L-M-B-2",
            "W": "L-R-B-1",
            "X": "R-M-B-2",
            "Y": "L-R-T-1",
            "Z": "R-P-H-0",
        },
    )


def allowed_left_positions() -> frozenset[str]:
    return frozenset({
        "L-R-T-1",
        "L-M-T-2",
        "L-I-T-3",
        "L-I-T-4",
        "L-R-H-1",
        "L-M-H-2",
        "L-I-H-3",
        "L-I-H-4",
    })


def allowed_right_positions() -> frozenset[str]:
    return frozenset({
        "R-I-T-4",
        "R-I-T-3",
        "R-M-T-2",
        "R-R-T-1",
        "R-I-H-4",
        "R-I-H-3",
        "R-M-H-2",
        "R-R-H-1",
    })


def make_builder() -> VowelSeedBuilder:
    return VowelSeedBuilder(
        evaluator=DummyEvaluator(),
        allowed_positions=allowed_left_positions(),
    )


def test_allowed_positions_are_exposed():
    builder = make_builder()

    assert (
        builder.allowed_positions
        == allowed_left_positions()
    )


def test_rejects_less_than_five_allowed_positions():
    with pytest.raises(
        ValueError,
        match="at least 5",
    ):
        VowelSeedBuilder(
            evaluator=DummyEvaluator(),
            allowed_positions=frozenset({
                "P1",
                "P2",
                "P3",
                "P4",
            }),
        )


def test_assign_vowels_moves_all_vowels_to_targets():
    builder = make_builder()
    layout = make_layout()

    targets = (
        "L-R-T-1",
        "L-M-T-2",
        "L-I-T-3",
        "L-I-T-4",
        "L-R-H-1",
    )

    result = builder._assign_vowels(
        layout,
        targets,
    )

    for vowel, target in zip(
        builder.VOWELS,
        targets,
        strict=True,
    ):
        assert result.position(vowel) == target


def test_assign_vowels_preserves_26_letters():
    builder = make_builder()

    result = builder._assign_vowels(
        make_layout(),
        (
            "L-R-T-1",
            "L-M-T-2",
            "L-I-T-3",
            "L-I-T-4",
            "L-R-H-1",
        ),
    )

    assert len(result) == 26

    assert set(result.letters()) == set(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    )


def test_assign_vowels_preserves_unique_positions():
    builder = make_builder()

    result = builder._assign_vowels(
        make_layout(),
        (
            "L-R-T-1",
            "L-M-T-2",
            "L-I-T-3",
            "L-I-T-4",
            "L-R-H-1",
        ),
    )

    positions = tuple(
        result.positions()
    )

    assert len(positions) == 26
    assert len(set(positions)) == 26


def test_assign_vowels_does_not_modify_original():
    builder = make_builder()
    layout = make_layout()

    original_mapping = dict(
        layout.items()
    )

    builder._assign_vowels(
        layout,
        (
            "L-R-T-1",
            "L-M-T-2",
            "L-I-T-3",
            "L-I-T-4",
            "L-R-H-1",
        ),
    )

    assert dict(layout.items()) == original_mapping


def test_assign_vowels_preserves_metadata():
    builder = make_builder()

    result = builder._assign_vowels(
        make_layout(),
        (
            "L-R-T-1",
            "L-M-T-2",
            "L-I-T-3",
            "L-I-T-4",
            "L-R-H-1",
        ),
    )

    assert result.name == "Vowel Seed Test"
    assert result.version == "1.0"
    assert result.layer == "L0"

    assert (
        result.description
        == "Vowel seed builder test layout"
    )


def test_assign_vowels_rejects_wrong_position_count():
    builder = make_builder()

    with pytest.raises(
        ValueError,
        match="exactly 5",
    ):
        builder._assign_vowels(
            make_layout(),
            (
                "L-R-T-1",
                "L-M-T-2",
            ),
        )


def test_assign_vowels_rejects_duplicate_targets():
    builder = make_builder()

    with pytest.raises(
        ValueError,
        match="unique",
    ):
        builder._assign_vowels(
            make_layout(),
            (
                "L-R-T-1",
                "L-R-T-1",
                "L-I-T-3",
                "L-I-T-4",
                "L-R-H-1",
            ),
        )


def test_generate_positions_respects_left_vowel_limits():
    allowed_positions = (
        allowed_left_positions()
        | allowed_right_positions()
    )

    builder = VowelSeedBuilder(
        evaluator=DummyEvaluator(),
        allowed_positions=allowed_positions,
    )

    candidate_positions = tuple(
        sorted(
            allowed_positions
        )
    )

    left_positions = tuple(
        position
        for position in candidate_positions
        if position.startswith("L-")
    )

    right_positions = tuple(
        position
        for position in candidate_positions
        if position.startswith("R-")
    )

    positions = tuple(
        builder._generate_vowel_positions(
            candidate_positions=candidate_positions,
            left_positions=left_positions,
            right_positions=right_positions,
            min_left_vowels=2,
            max_left_vowels=3,
        )
    )

    assert positions

    for vowel_positions in positions:
        left_count = sum(
            position.startswith("L-")
            for position in vowel_positions
        )

        assert left_count in {
            2,
            3,
        }


def test_generate_positions_without_limits_preserves_all():
    builder = make_builder()

    candidate_positions = tuple(
        sorted(
            allowed_left_positions()
        )
    )

    positions = tuple(
        builder._generate_vowel_positions(
            candidate_positions=candidate_positions,
            left_positions=candidate_positions,
            right_positions=(),
            min_left_vowels=None,
            max_left_vowels=None,
        )
    )

    assert len(positions) == 6720