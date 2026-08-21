# tests/test_candidate_evaluation.py

import pytest

from models.candidate_evaluation import CandidateEvaluation
from models.candidate_score import CandidateScore, CandidateScoreWeights
from models.constraint_evaluation import ConstraintEvaluation
from models.layout import Layout
from models.layout_evaluation import LayoutEvaluation


def make_layout() -> Layout:
    mapping = {
        chr(ord("A") + index): f"P{index}"
        for index in range(26)
    }

    return Layout(
        name="test",
        version="1",
        layer="L0",
        description="test layout",
        mapping=mapping,
    )


def make_constraint_evaluation() -> ConstraintEvaluation:
    return ConstraintEvaluation(
        violations=(),
    )


def make_layout_evaluation() -> LayoutEvaluation:
    return LayoutEvaluation(
        total_cost=30.0,
        evaluated_weight=100.0,
        skipped_weight=0.0,
        transitions=(),
    )


def make_candidate_score() -> CandidateScore:
    return CandidateScore(
        transition_score=0.3,
        finger_load_score=0.1,
        weights=CandidateScoreWeights(
            transition_weight=2.0,
            finger_load_weight=4.0,
        ),
    )


def test_candidate_evaluation_is_valid():
    evaluation = CandidateEvaluation(
        layout=make_layout(),
        constraint_evaluation=make_constraint_evaluation(),
        layout_evaluation=make_layout_evaluation(),
        candidate_score=make_candidate_score(),
    )

    assert evaluation.is_valid is True


def test_candidate_score_is_preserved():
    candidate_score = make_candidate_score()

    evaluation = CandidateEvaluation(
        layout=make_layout(),
        constraint_evaluation=make_constraint_evaluation(),
        layout_evaluation=make_layout_evaluation(),
        candidate_score=candidate_score,
    )

    assert evaluation.candidate_score == candidate_score


def test_score_returns_combined_total():
    evaluation = CandidateEvaluation(
        layout=make_layout(),
        constraint_evaluation=make_constraint_evaluation(),
        layout_evaluation=make_layout_evaluation(),
        candidate_score=make_candidate_score(),
    )

    # transition:
    # 0.3 * 2.0 = 0.6
    #
    # finger load:
    # 0.1 * 4.0 = 0.4
    #
    # total = 1.0
    assert evaluation.score == pytest.approx(1.0)


def test_score_is_none_without_candidate_score():
    evaluation = CandidateEvaluation(
        layout=make_layout(),
        constraint_evaluation=make_constraint_evaluation(),
        layout_evaluation=None,
        candidate_score=None,
    )

    assert evaluation.score is None


def test_candidate_evaluation_is_immutable():
    evaluation = CandidateEvaluation(
        layout=make_layout(),
        constraint_evaluation=make_constraint_evaluation(),
        layout_evaluation=make_layout_evaluation(),
        candidate_score=make_candidate_score(),
    )

    with pytest.raises(AttributeError):
        evaluation.candidate_score = None