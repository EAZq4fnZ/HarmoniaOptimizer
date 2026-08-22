# tests/test_swap_move.py

import pytest

from models.swap_move import SwapMove


def test_swap_move_attributes():
    move = SwapMove(
        first_letter="A",
        second_letter="B",
    )

    assert move.first_letter == "A"
    assert move.second_letter == "B"


def test_swap_move_normalizes_to_uppercase():
    move = SwapMove(
        first_letter="a",
        second_letter="b",
    )

    assert move.first_letter == "A"
    assert move.second_letter == "B"


def test_swap_move_exposes_letters():
    move = SwapMove(
        first_letter="A",
        second_letter="T",
    )

    assert move.letters == (
        "A",
        "T",
    )


def test_swap_move_rejects_same_letter():
    with pytest.raises(ValueError):
        SwapMove(
            first_letter="A",
            second_letter="A",
        )


def test_swap_move_rejects_invalid_first_letter():
    with pytest.raises(ValueError):
        SwapMove(
            first_letter="?",
            second_letter="A",
        )


def test_swap_move_rejects_invalid_second_letter():
    with pytest.raises(ValueError):
        SwapMove(
            first_letter="A",
            second_letter="?",
        )


def test_swap_move_rejects_multiple_characters():
    with pytest.raises(ValueError):
        SwapMove(
            first_letter="AB",
            second_letter="C",
        )


def test_swap_move_is_immutable():
    move = SwapMove(
        first_letter="A",
        second_letter="B",
    )

    with pytest.raises(AttributeError):
        move.first_letter = "C"


def test_swap_move_is_hashable():
    move = SwapMove(
        first_letter="A",
        second_letter="B",
    )

    values = {move}

    assert move in values