# tests/test_optimization_result.py

import pytest

from models.candidate_evaluation import CandidateEvaluation
from models.candidate_score import (
    CandidateScore,
    CandidateScoreWeights,
)
from models.constraint_evaluation import ConstraintEvaluation
from models.layout import Layout
from models.optimization_result import OptimizationResult
from models.optimization_step import OptimizationStep
from models.swap_move import SwapMove


def make_layout(
    name: str,
) -> Layout:
    return Layout(
        name=name,
        version="1",
        layer="L0",
        description="optimization result test",
        mapping={
            chr(ord("A") + index): f"P{index}"
            for index in range(26)
        },
    )


def make_evaluation(
    name: str,
    score: float,
) -> CandidateEvaluation:
    return CandidateEvaluation(
        layout=make_layout(name),
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


def test_result_preserves_evaluations():
    initial = make_evaluation("initial", 10.0)
    final = make_evaluation("final", 4.0)

    result = OptimizationResult(
        initial_evaluation=initial,
        final_evaluation=final,
        steps=(),
    )

    assert result.initial_evaluation == initial
    assert result.final_evaluation == final


def test_result_exposes_scores():
    result = OptimizationResult(
        initial_evaluation=make_evaluation(
            "initial",
            10.0,
        ),
        final_evaluation=make_evaluation(
            "final",
            4.0,
        ),
        steps=(),
    )

    assert result.initial_score == 10.0
    assert result.final_score == 4.0


def test_result_calculates_improvement():
    result = OptimizationResult(
        initial_evaluation=make_evaluation(
            "initial",
            10.0,
        ),
        final_evaluation=make_evaluation(
            "final",
            4.0,
        ),
        steps=(),
    )

    assert result.improvement == pytest.approx(6.0)
    assert result.improved is True


def test_result_reports_no_improvement():
    evaluation = make_evaluation(
        "same",
        5.0,
    )

    result = OptimizationResult(
        initial_evaluation=evaluation,
        final_evaluation=evaluation,
        steps=(),
    )

    assert result.improvement == 0.0
    assert result.improved is False


def test_iteration_count():
    first = make_evaluation("first", 8.0)
    second = make_evaluation("second", 5.0)

    result = OptimizationResult(
        initial_evaluation=make_evaluation(
            "initial",
            10.0,
        ),
        final_evaluation=second,
        steps=(
            OptimizationStep(
                iteration=1,
                move=SwapMove(
                    first_letter="A",
                    second_letter="B",
                ),
                evaluation=first,
            ),
            OptimizationStep(
                iteration=2,
                move=SwapMove(
                    first_letter="C",
                    second_letter="D",
                ),
                evaluation=second,
            ),
        ),
    )

    assert result.iteration_count == 2


def test_optimization_result_is_immutable():
    result = OptimizationResult(
        initial_evaluation=make_evaluation(
            "initial",
            10.0,
        ),
        final_evaluation=make_evaluation(
            "final",
            5.0,
        ),
        steps=(),
    )

    with pytest.raises(AttributeError):
        result.steps = ()