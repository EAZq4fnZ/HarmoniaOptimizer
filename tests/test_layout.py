# tests/test_layout.py

from pathlib import Path

import pytest

from models.layout import Layout


def make_valid_layout() -> Layout:
    mapping = {
        "A": "L-M-H",
        "B": "L-M-T",
        "C": "L-R-H",
        "D": "L-R-T",
        "E": "L-I-H",
        "F": "L-P-H",
        "G": "L-I-T",
        "H": "L-R-B",
        "I": "L-M-T2",
        "J": "R-M-H",
        "K": "L-I-U",
        "L": "R-I-H",
        "M": "R-P-H",
        "N": "R-I-U",
        "O": "R-M-H2",
        "P": "R-R-B",
        "Q": "R-I-B",
        "R": "L-I-U2",
        "S": "L-I-H2",
        "T": "L-I-H3",
        "U": "R-I-H2",
        "V": "L-R-U",
        "W": "L-I-B",
        "X": "R-R-U",
        "Y": "L-M-B",
        "Z": "R-M-B",
    }

    return Layout(
        name="Test Layout",
        version="0.1.0",
        layer="L0",
        description="Test layout",
        mapping=mapping,
    )


def test_layout_has_26_letters():
    layout = make_valid_layout()

    assert len(layout) == 26


def test_layout_contains_all_alphabet():
    layout = make_valid_layout()

    assert set(layout.letters()) == set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def test_position_lookup():
    layout = make_valid_layout()

    assert layout.position("A") == "L-M-H"


def test_position_lookup_is_case_insensitive():
    layout = make_valid_layout()

    assert layout.position("a") == "L-M-H"


def test_reverse_lookup():
    layout = make_valid_layout()

    assert layout.letter("L-M-H") == "A"


def test_contains():
    layout = make_valid_layout()

    assert "A" in layout
    assert "a" in layout
    assert "@" not in layout


def test_getitem():
    layout = make_valid_layout()

    assert layout["A"] == "L-M-H"


def test_items():
    layout = make_valid_layout()

    items = dict(layout.items())

    assert items["A"] == "L-M-H"


def test_positions_are_unique():
    layout = make_valid_layout()

    positions = list(layout.positions())

    assert len(positions) == len(set(positions))


def test_layout_rejects_missing_letter():
    mapping = make_valid_layout().mapping.copy()
    del mapping["Z"]

    with pytest.raises(
        ValueError,
        match="Layout must contain exactly 26 letters",
    ):
        Layout(
            name="Invalid Layout",
            version="0.1.0",
            layer="L0",
            description="Missing Z",
            mapping=mapping,
        )


def test_layout_rejects_duplicate_position():
    mapping = make_valid_layout().mapping.copy()
    mapping["B"] = mapping["A"]

    with pytest.raises(
        ValueError,
        match="Duplicate logical positions detected",
    ):
        Layout(
            name="Invalid Layout",
            version="0.1.0",
            layer="L0",
            description="Duplicate position",
            mapping=mapping,
        )