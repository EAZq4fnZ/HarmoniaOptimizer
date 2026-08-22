# tests/test_swap_candidate.py

import pytest

from models.layout import Layout
from models.swap_candidate import SwapCandidate
from models.swap_move import SwapMove


def make_layout() -> Layout:
    return Layout(
        name="Swap Candidate Test",
        version="0.1.0",
        layer="L0",
        description="Swap candidate test layout",
        mapping={
            chr(ord("A") + index): f"P{index}"
            for index in range(26)
        },
    )


def test_swap_candidate_attributes():
    move = SwapMove(
        first_letter="A",
        second_letter="B",
    )

    layout = make_layout()

    candidate = SwapCandidate(
        move=move,
        layout=layout,
    )

    assert candidate.move == move
    assert candidate.layout == layout


def test_swap_candidate_preserves_move_letters():
    candidate = SwapCandidate(
        move=SwapMove(
            first_letter="A",
            second_letter="T",
        ),
        layout=make_layout(),
    )

    assert candidate.move.first_letter == "A"
    assert candidate.move.second_letter == "T"


def test_swap_candidate_preserves_layout():
    layout = make_layout()

    candidate = SwapCandidate(
        move=SwapMove(
            first_letter="A",
            second_letter="B",
        ),
        layout=layout,
    )

    assert candidate.layout is layout


def test_swap_candidate_is_immutable():
    candidate = SwapCandidate(
        move=SwapMove(
            first_letter="A",
            second_letter="B",
        ),
        layout=make_layout(),
    )

    with pytest.raises(AttributeError):
        candidate.move = SwapMove(
            first_letter="C",
            second_letter="D",
        )


def test_swap_candidate_equality():
    layout = make_layout()

    candidate1 = SwapCandidate(
        move=SwapMove(
            first_letter="A",
            second_letter="B",
        ),
        layout=layout,
    )

    candidate2 = SwapCandidate(
        move=SwapMove(
            first_letter="A",
            second_letter="B",
        ),
        layout=layout,
    )

    assert candidate1 == candidate2


def test_different_moves_are_not_equal():
    layout = make_layout()

    candidate1 = SwapCandidate(
        move=SwapMove(
            first_letter="A",
            second_letter="B",
        ),
        layout=layout,
    )

    candidate2 = SwapCandidate(
        move=SwapMove(
            first_letter="A",
            second_letter="C",
        ),
        layout=layout,
    )

    assert candidate1 != candidate2