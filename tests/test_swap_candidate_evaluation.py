# tests/test_swap_candidate_evaluation.py

import pytest

from models.candidate_evaluation import CandidateEvaluation
from models.candidate_score import (
    CandidateScore,
    CandidateScoreWeights,
)
from models.constraint_evaluation import ConstraintEvaluation
from models.layout import Layout
from models.swap_candidate import SwapCandidate
from models.swap_candidate_evaluation import SwapCandidateEvaluation
from models.swap_move import SwapMove


def make_layout() -> Layout:
    return Layout(
        name="Swap Candidate Evaluation Test",
        version="0.1.0",
        layer="L0",
        description="Swap candidate evaluation test",
        mapping={
            chr(ord("A") + index): f"P{index}"
            for index in range(26)
        },
    )


def make_candidate() -> SwapCandidate:
    return SwapCandidate(
        move=SwapMove(
            first_letter="A",
            second_letter="B",
        ),
        layout=make_layout(),
    )


def make_evaluation(
    layout: Layout,
    score: float = 5.0,
) -> CandidateEvaluation:
    return CandidateEvaluation(
        layout=layout,
        constraint_evaluation=ConstraintEvaluation(
            violations=(),
        ),
        layout_evaluation=None,
        candidate_score=CandidateScore(
            transition_score=score,
            finger_load_score=0.0,
            weights=CandidateScoreWeights(
                transition_weight=1.0,
                finger_load_weight=1.0,
            ),
        ),
    )


def make_swap_candidate_evaluation(
    score: float = 5.0,
) -> SwapCandidateEvaluation:
    candidate = make_candidate()

    evaluation = make_evaluation(
        candidate.layout,
        score,
    )

    return SwapCandidateEvaluation(
        candidate=candidate,
        evaluation=evaluation,
    )


def test_swap_candidate_evaluation_attributes():
    candidate = make_candidate()

    evaluation = make_evaluation(
        candidate.layout,
    )

    result = SwapCandidateEvaluation(
        candidate=candidate,
        evaluation=evaluation,
    )

    assert result.candidate == candidate
    assert result.evaluation == evaluation


def test_move_is_exposed():
    result = make_swap_candidate_evaluation()

    assert result.move == result.candidate.move
    assert result.move.first_letter == "A"
    assert result.move.second_letter == "B"


def test_layout_is_exposed():
    result = make_swap_candidate_evaluation()

    assert result.layout == result.candidate.layout


def test_validity_is_exposed():
    result = make_swap_candidate_evaluation()

    assert result.is_valid is True


def test_score_is_exposed():
    result = make_swap_candidate_evaluation(
        score=3.5,
    )

    assert result.score == pytest.approx(3.5)


def test_swap_candidate_evaluation_is_immutable():
    result = make_swap_candidate_evaluation()

    with pytest.raises(AttributeError):
        result.candidate = make_candidate()