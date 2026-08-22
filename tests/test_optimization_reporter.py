# tests/test_optimization_reporter.py

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
from reporting.optimization_reporter import OptimizationReporter


def make_layout(
    name: str,
) -> Layout:
    return Layout(
        name=name,
        version="1",
        layer="L0",
        description="optimization reporter test",
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


def make_result_with_steps() -> OptimizationResult:
    initial = make_evaluation(
        "initial",
        10.0,
    )

    first = make_evaluation(
        "first",
        7.0,
    )

    second = make_evaluation(
        "second",
        3.0,
    )

    return OptimizationResult(
        initial_evaluation=initial,
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


def test_reporter_returns_string():
    reporter = OptimizationReporter()

    report = reporter.format(
        make_result_with_steps()
    )

    assert isinstance(report, str)


def test_report_contains_title():
    reporter = OptimizationReporter()

    report = reporter.format(
        make_result_with_steps()
    )

    assert "Optimization Result" in report


def test_report_contains_scores():
    reporter = OptimizationReporter()

    report = reporter.format(
        make_result_with_steps()
    )

    assert "Initial score: 10.000000" in report
    assert "Final score:   3.000000" in report
    assert "Improvement:   7.000000" in report


def test_report_contains_iteration_count():
    reporter = OptimizationReporter()

    report = reporter.format(
        make_result_with_steps()
    )

    assert "Iterations:    2" in report


def test_report_contains_swap_moves():
    reporter = OptimizationReporter()

    report = reporter.format(
        make_result_with_steps()
    )

    assert "1. A <-> B" in report
    assert "2. C <-> D" in report


def test_report_contains_step_scores():
    reporter = OptimizationReporter()

    report = reporter.format(
        make_result_with_steps()
    )

    assert "score: 7.000000" in report
    assert "score: 3.000000" in report


def test_report_without_steps_shows_none():
    evaluation = make_evaluation(
        "same",
        5.0,
    )

    result = OptimizationResult(
        initial_evaluation=evaluation,
        final_evaluation=evaluation,
        steps=(),
    )

    reporter = OptimizationReporter()

    report = reporter.format(result)

    assert "Iterations:    0" in report
    assert "Accepted moves" in report
    assert "None" in report


def test_format_score_handles_none():
    assert (
        OptimizationReporter._format_score(None)
        == "N/A"
    )