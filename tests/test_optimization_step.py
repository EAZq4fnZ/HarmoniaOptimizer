# tests/test_optimization_step.py

import pytest

from models.candidate_evaluation import CandidateEvaluation
from models.candidate_score import (
    CandidateScore,
    CandidateScoreWeights,
)
from models.constraint_evaluation import ConstraintEvaluation
from models.layout import Layout
from models.optimization_step import OptimizationStep


def make_layout() -> Layout:
    return Layout(
        name="Test",
        version="1",
        layer="L0",
        description="optimization step test",
        mapping={
            chr(ord("A") + index): f"P{index}"
            for index in range(26)
        },
    )


def make_evaluation(
    score: float = 5.0,
) -> CandidateEvaluation:
    return CandidateEvaluation(
        layout=make_layout(),
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


def test_optimization_step_attributes():
    evaluation = make_evaluation()

    step = OptimizationStep(
        iteration=1,
        evaluation=evaluation,
    )

    assert step.iteration == 1
    assert step.evaluation == evaluation


def test_optimization_step_exposes_score():
    step = OptimizationStep(
        iteration=1,
        evaluation=make_evaluation(3.0),
    )

    assert step.score == 3.0


def test_iteration_must_be_positive():
    with pytest.raises(ValueError):
        OptimizationStep(
            iteration=0,
            evaluation=make_evaluation(),
        )


def test_optimization_step_is_immutable():
    step = OptimizationStep(
        iteration=1,
        evaluation=make_evaluation(),
    )

    with pytest.raises(AttributeError):
        step.iteration = 2