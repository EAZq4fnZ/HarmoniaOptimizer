# tests/test_layout_mutator.py

import pytest

from models.layout import Layout
from optimizer.layout_mutator import LayoutMutator


def make_layout() -> Layout:
    return Layout(
        name="Mutation Test Layout",
        version="0.1.0",
        layer="L0",
        description="Layout mutator test",
        mapping={
            "A": "L-I-H-3",
            "B": "R-I-H-3",
            "C": "L-R-H-1",
            "D": "L-M-T-2",
            "E": "L-M-H-2",
            "F": "L-I-T-3",
            "G": "L-I-H-4",
            "H": "L-I-T-4",
            "I": "R-I-T-3",
            "J": "R-I-H-4",
            "K": "R-I-T-4",
            "L": "R-M-H-2",
            "M": "R-R-H-1",
            "N": "R-M-T-2",
            "O": "R-M-B-2",
            "P": "R-R-T-1",
            "Q": "L-P-H-0",
            "R": "L-R-T-1",
            "S": "L-M-B-2",
            "T": "L-I-B-3",
            "U": "R-R-B-1",
            "V": "R-I-B-3",
            "W": "R-P-H-0",
            "X": "L-P-T-0",
            "Y": "L-P-B-0",
            "Z": "R-P-T-0",
        },
    )


def test_swap_returns_new_layout():
    layout = make_layout()
    mutator = LayoutMutator()

    result = mutator.swap(
        layout,
        "A",
        "B",
    )

    assert isinstance(result, Layout)
    assert result is not layout


def test_swap_exchanges_positions():
    layout = make_layout()
    mutator = LayoutMutator()

    result = mutator.swap(
        layout,
        "A",
        "B",
    )

    assert result.position("A") == "R-I-H-3"
    assert result.position("B") == "L-I-H-3"


def test_swap_preserves_other_letters():
    layout = make_layout()
    mutator = LayoutMutator()

    result = mutator.swap(
        layout,
        "A",
        "B",
    )

    for letter in layout.letters():
        if letter not in {"A", "B"}:
            assert result.position(letter) == layout.position(letter)


def test_swap_does_not_modify_original_layout():
    layout = make_layout()
    mutator = LayoutMutator()

    mutator.swap(
        layout,
        "A",
        "B",
    )

    assert layout.position("A") == "L-I-H-3"
    assert layout.position("B") == "R-I-H-3"


def test_swap_preserves_metadata():
    layout = make_layout()
    mutator = LayoutMutator()

    result = mutator.swap(
        layout,
        "A",
        "B",
    )

    assert result.name == layout.name
    assert result.version == layout.version
    assert result.layer == layout.layer
    assert result.description == layout.description


def test_swap_is_case_insensitive():
    layout = make_layout()
    mutator = LayoutMutator()

    result = mutator.swap(
        layout,
        "a",
        "b",
    )

    assert result.position("A") == "R-I-H-3"
    assert result.position("B") == "L-I-H-3"


def test_swap_same_letter_returns_equivalent_layout():
    layout = make_layout()
    mutator = LayoutMutator()

    result = mutator.swap(
        layout,
        "A",
        "A",
    )

    assert result.mapping == layout.mapping
    assert result is not layout


def test_swap_rejects_unknown_first_letter():
    layout = make_layout()
    mutator = LayoutMutator()

    with pytest.raises(
        KeyError,
        match="Unknown letter",
    ):
        mutator.swap(
            layout,
            "?",
            "A",
        )


def test_swap_rejects_unknown_second_letter():
    layout = make_layout()
    mutator = LayoutMutator()

    with pytest.raises(
        KeyError,
        match="Unknown letter",
    ):
        mutator.swap(
            layout,
            "A",
            "?",
        )


def test_double_swap_restores_mapping():
    layout = make_layout()
    mutator = LayoutMutator()

    swapped = mutator.swap(
        layout,
        "A",
        "B",
    )

    restored = mutator.swap(
        swapped,
        "A",
        "B",
    )

    assert restored.mapping == layout.mapping