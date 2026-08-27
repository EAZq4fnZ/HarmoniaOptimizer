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


def test_balanced_candidate_count_is_376320():
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

    count = builder._count_candidate_positions(
        candidate_positions=candidate_positions,
        min_left_vowels=2,
        max_left_vowels=3,
    )

    assert count == 376320


def test_balanced_generator_produces_expected_count():
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

    count = sum(
        1
        for _ in builder._generate_vowel_positions(
            candidate_positions=candidate_positions,
            left_positions=left_positions,
            right_positions=right_positions,
            min_left_vowels=2,
            max_left_vowels=3,
        )
    )

    assert count == 376320


def test_assign_vowels_mapping_matches_assign_vowels() -> None:
    builder = make_builder()
    layout = make_layout()

    vowel_positions = (
        "L-R-T-1",
        "L-M-T-2",
        "L-I-T-3",
        "L-R-H-1",
        "L-M-H-2",
    )

    mapped = builder._assign_vowels_mapping(
        layout=layout,
        vowel_positions=vowel_positions,
    )

    assigned = builder._assign_vowels(
        layout=layout,
        vowel_positions=vowel_positions,
    )

    assert mapped == assigned.mapping


def test_mapping_to_indexed_positions_matches_mapping() -> None:
    builder = make_builder()
    layout = make_layout()

    positions = builder._mapping_to_indexed_positions(
        layout.mapping
    )

    for letter, position in layout.mapping.items():
        index = (
            ord(letter.upper())
            - ord("A")
        )

        assert positions[index] == position

def test_assign_vowels_position_indexed_matches_mapping() -> None:
    builder = make_builder()
    layout = make_layout()

    vowel_positions = (
        "L-R-T-1",
        "L-M-T-2",
        "L-I-T-3",
        "L-R-H-1",
        "L-M-H-2",
    )

    expected_mapping = (
        builder._assign_vowels_mapping(
            layout=layout,
            vowel_positions=vowel_positions,
        )
    )

    base_string_positions = (
        builder._layout_to_indexed_positions(
            layout
        )
    )

    position_ids_by_index = tuple(
        sorted(
            position
            for position
            in base_string_positions
            if position is not None
        )
    )

    position_indexes = {
        position: index
        for index, position
        in enumerate(
            position_ids_by_index
        )
    }

    base_position_indexes = [
        (
            -1
            if position is None
            else position_indexes[
                position
            ]
        )
        for position
        in base_string_positions
    ]

    original_vowel_positions = frozenset(
        base_position_indexes[
            vowel_index
        ]
        for vowel_index
        in builder.VOWEL_INDEXES
    )

    letter_index_by_position = [
        -1
    ] * len(
        position_ids_by_index
    )

    for (
        letter_index,
        position_index,
    ) in enumerate(
        base_position_indexes
    ):
        if position_index >= 0:
            letter_index_by_position[
                position_index
            ] = letter_index

    vowel_position_indexes = tuple(
        position_indexes[
            position
        ]
        for position
        in vowel_positions
    )

    result = (
        builder
        ._assign_vowels_position_indexed(
            base_positions=base_position_indexes,
            vowel_position_indexes=(
                vowel_position_indexes
            ),
            original_vowel_positions=(
                original_vowel_positions
            ),
            letter_index_by_position=tuple(
                letter_index_by_position
            ),
        )
    )

    result_mapping = (
        builder._position_indexed_to_mapping(
            result,
            position_ids_by_index,
        )
    )

    assert result_mapping == expected_mapping

def test_generate_vowel_position_indexes_matches_string_generator() -> None:
    builder = make_builder()

    candidate_positions = (
        "L-I-H-1",
        "L-I-H-2",
        "L-I-H-3",
        "R-I-H-1",
        "R-I-H-2",
        "R-I-H-3",
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

    position_indexes = {
        position: index
        for index, position in enumerate(
            candidate_positions
        )
    }

    candidate_position_indexes = tuple(
        position_indexes[position]
        for position in candidate_positions
    )

    left_position_indexes = tuple(
        position_indexes[position]
        for position in left_positions
    )

    right_position_indexes = tuple(
        position_indexes[position]
        for position in right_positions
    )

    string_candidates = list(
        builder._generate_vowel_positions(
            candidate_positions=candidate_positions,
            left_positions=left_positions,
            right_positions=right_positions,
            min_left_vowels=2,
            max_left_vowels=3,
        )
    )

    integer_candidates = list(
        builder._generate_vowel_position_indexes(
            candidate_position_indexes=(
                candidate_position_indexes
            ),
            left_position_indexes=(
                left_position_indexes
            ),
            right_position_indexes=(
                right_position_indexes
            ),
            min_left_vowels=2,
            max_left_vowels=3,
        )
    )

    converted_string_candidates = [
        tuple(
            position_indexes[position]
            for position in candidate
        )
        for candidate in string_candidates
    ]

    assert (
        integer_candidates
        == converted_string_candidates
    )

def test_assign_vowels_position_indexed_fast_matches_checked() -> None:
    builder = make_builder()
    layout = make_layout()

    base_string_positions = (
        builder._layout_to_indexed_positions(
            layout
        )
    )

    position_ids = tuple(
        sorted(
            position
            for position in base_string_positions
            if position is not None
        )
    )

    position_indexes = {
        position: index
        for index, position in enumerate(
            position_ids
        )
    }

    base_positions = [
        (
            -1
            if position is None
            else position_indexes[position]
        )
        for position in base_string_positions
    ]

    original_vowel_positions = frozenset(
        base_positions[index]
        for index in builder.VOWEL_INDEXES
    )

    original_vowel_positions_sorted = tuple(
        sorted(
            original_vowel_positions
        )
    )

    letter_index_by_position = [
        -1
    ] * len(position_ids)

    for (
        letter_index,
        position_index,
    ) in enumerate(
        base_positions
    ):
        if position_index >= 0:
            letter_index_by_position[
                position_index
            ] = letter_index

    vowel_positions = (
        "L-R-T-1",
        "L-M-T-2",
        "L-I-T-3",
        "L-I-T-4",
        "L-R-H-1",
    )

    vowel_position_indexes = tuple(
        position_indexes[position]
        for position in vowel_positions
    )

    checked = (
        builder
        ._assign_vowels_position_indexed(
            base_positions=base_positions,
            vowel_position_indexes=(
                vowel_position_indexes
            ),
            original_vowel_positions=(
                original_vowel_positions
            ),
            letter_index_by_position=tuple(
                letter_index_by_position
            ),
        )
    )

    fast = (
        builder
        ._assign_vowels_position_indexed_fast(
            base_positions=base_positions,
            vowel_position_indexes=(
                vowel_position_indexes
            ),
            original_vowel_positions=(
                original_vowel_positions
            ),
            original_vowel_positions_sorted=(
                original_vowel_positions_sorted
            ),
            letter_index_by_position=tuple(
                letter_index_by_position
            ),
        )
    )

    assert fast == checked