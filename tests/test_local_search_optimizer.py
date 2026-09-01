# tests/test_local_search_optimizer.py

from models.candidate_evaluation import CandidateEvaluation
from models.candidate_score import (
    CandidateScore,
    CandidateScoreWeights,
)
from models.constraint_evaluation import ConstraintEvaluation
from models.layout import Layout
from models.optimization_result import OptimizationResult
from models.swap_candidate import SwapCandidate
from models.swap_move import SwapMove
from optimizer.local_search_optimizer import LocalSearchOptimizer


def make_layout(
    name: str,
) -> Layout:
    mapping = {
        chr(ord("A") + index): f"P{index}"
        for index in range(26)
    }

    return Layout(
        name=name,
        version="1",
        layer="L0",
        description="local search optimizer test",
        mapping=mapping,
    )


def make_evaluation(
    layout: Layout,
    score: float,
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


def make_swap_candidate(
    layout: Layout,
    first_letter: str,
    second_letter: str,
) -> SwapCandidate:
    return SwapCandidate(
        move=SwapMove(
            first_letter=first_letter,
            second_letter=second_letter,
        ),
        layout=layout,
    )


class FakeCandidateEvaluator:
    def __init__(
        self,
        scores: dict[str, float],
    ) -> None:
        self._scores = scores
        self.evaluated_layouts: list[str] = []

    def evaluate(
        self,
        layout,
        transition_statistics,
        character_statistics,
        trigram_statistics=None,
    ):
        self.evaluated_layouts.append(
            layout.name
        )

        return make_evaluation(
            layout,
            self._scores[layout.name],
        )


class FakeCandidateGenerator:
    def __init__(
        self,
        candidates: dict[
            str,
            tuple[SwapCandidate, ...],
        ],
    ) -> None:
        self._candidates = candidates
        self.generated_from: list[str] = []

    def generate_candidates(
        self,
        layout,
    ):
        self.generated_from.append(
            layout.name
        )

        return self._candidates.get(
            layout.name,
            (),
        )


def test_optimizer_returns_optimization_result():
    initial = make_layout("initial")

    evaluator = FakeCandidateEvaluator(
        {
            "initial": 5.0,
        }
    )

    optimizer = LocalSearchOptimizer(
        candidate_evaluator=evaluator,
        candidate_generator=FakeCandidateGenerator({}),
    )

    result = optimizer.optimize(
        layout=initial,
        transition_statistics=None,
        character_statistics=None,
    )

    assert isinstance(result, OptimizationResult)


def test_optimizer_returns_initial_layout_when_no_improvement():
    initial = make_layout("initial")
    worse = make_layout("worse")

    evaluator = FakeCandidateEvaluator(
        {
            "initial": 5.0,
            "worse": 10.0,
        }
    )

    generator = FakeCandidateGenerator(
        {
            "initial": (
                make_swap_candidate(
                    worse,
                    "A",
                    "B",
                ),
            ),
        }
    )

    optimizer = LocalSearchOptimizer(
        candidate_evaluator=evaluator,
        candidate_generator=generator,
    )

    result = optimizer.optimize(
        layout=initial,
        transition_statistics=None,
        character_statistics=None,
    )

    assert result.initial_evaluation.layout == initial
    assert result.final_evaluation.layout == initial
    assert result.initial_score == 5.0
    assert result.final_score == 5.0
    assert result.steps == ()
    assert result.improved is False


def test_optimizer_accepts_better_candidate():
    initial = make_layout("initial")
    better = make_layout("better")

    evaluator = FakeCandidateEvaluator(
        {
            "initial": 10.0,
            "better": 5.0,
        }
    )

    generator = FakeCandidateGenerator(
        {
            "initial": (
                make_swap_candidate(
                    better,
                    "A",
                    "B",
                ),
            ),
            "better": (),
        }
    )

    optimizer = LocalSearchOptimizer(
        candidate_evaluator=evaluator,
        candidate_generator=generator,
    )

    result = optimizer.optimize(
        layout=initial,
        transition_statistics=None,
        character_statistics=None,
    )

    assert result.final_evaluation.layout == better
    assert result.final_score == 5.0
    assert result.improved is True
    assert result.improvement == 5.0
    assert result.iteration_count == 1

    assert result.steps[0].iteration == 1
    assert result.steps[0].move == SwapMove(
        first_letter="A",
        second_letter="B",
    )
    assert result.steps[0].evaluation.layout == better
    assert result.steps[0].score == 5.0


def test_optimizer_repeats_until_local_optimum():
    initial = make_layout("initial")
    second = make_layout("second")
    third = make_layout("third")

    evaluator = FakeCandidateEvaluator(
        {
            "initial": 10.0,
            "second": 7.0,
            "third": 3.0,
        }
    )

    generator = FakeCandidateGenerator(
        {
            "initial": (
                make_swap_candidate(
                    second,
                    "A",
                    "B",
                ),
            ),
            "second": (
                make_swap_candidate(
                    third,
                    "C",
                    "D",
                ),
            ),
            "third": (),
        }
    )

    optimizer = LocalSearchOptimizer(
        candidate_evaluator=evaluator,
        candidate_generator=generator,
    )

    result = optimizer.optimize(
        layout=initial,
        transition_statistics=None,
        character_statistics=None,
    )

    assert result.initial_score == 10.0
    assert result.final_score == 3.0
    assert result.improvement == 7.0
    assert result.iteration_count == 2

    assert tuple(
        step.score
        for step in result.steps
    ) == (
        7.0,
        3.0,
    )

    assert tuple(
        step.iteration
        for step in result.steps
    ) == (
        1,
        2,
    )

    assert result.steps[0].move == SwapMove(
        first_letter="A",
        second_letter="B",
    )

    assert result.steps[1].move == SwapMove(
        first_letter="C",
        second_letter="D",
    )

    assert result.final_evaluation.layout == third


def test_optimizer_selects_best_candidate():
    initial = make_layout("initial")
    candidate1 = make_layout("candidate1")
    candidate2 = make_layout("candidate2")
    candidate3 = make_layout("candidate3")

    evaluator = FakeCandidateEvaluator(
        {
            "initial": 10.0,
            "candidate1": 8.0,
            "candidate2": 4.0,
            "candidate3": 6.0,
        }
    )

    generator = FakeCandidateGenerator(
        {
            "initial": (
                make_swap_candidate(
                    candidate1,
                    "A",
                    "B",
                ),
                make_swap_candidate(
                    candidate2,
                    "C",
                    "D",
                ),
                make_swap_candidate(
                    candidate3,
                    "E",
                    "F",
                ),
            ),
            "candidate2": (),
        }
    )

    optimizer = LocalSearchOptimizer(
        candidate_evaluator=evaluator,
        candidate_generator=generator,
    )

    result = optimizer.optimize(
        layout=initial,
        transition_statistics=None,
        character_statistics=None,
    )

    assert result.final_evaluation.layout == candidate2
    assert result.final_score == 4.0
    assert result.iteration_count == 1

    assert result.steps[0].move == SwapMove(
        first_letter="C",
        second_letter="D",
    )


def test_optimizer_does_not_accept_equal_score():
    initial = make_layout("initial")
    equal = make_layout("equal")

    evaluator = FakeCandidateEvaluator(
        {
            "initial": 5.0,
            "equal": 5.0,
        }
    )

    generator = FakeCandidateGenerator(
        {
            "initial": (
                make_swap_candidate(
                    equal,
                    "A",
                    "B",
                ),
            ),
        }
    )

    optimizer = LocalSearchOptimizer(
        candidate_evaluator=evaluator,
        candidate_generator=generator,
    )

    result = optimizer.optimize(
        layout=initial,
        transition_statistics=None,
        character_statistics=None,
    )

    assert result.final_evaluation.layout == initial
    assert result.final_score == 5.0
    assert result.steps == ()
    assert result.improved is False


def test_optimizer_respects_max_iterations():
    initial = make_layout("initial")
    second = make_layout("second")
    third = make_layout("third")

    evaluator = FakeCandidateEvaluator(
        {
            "initial": 10.0,
            "second": 7.0,
            "third": 3.0,
        }
    )

    generator = FakeCandidateGenerator(
        {
            "initial": (
                make_swap_candidate(
                    second,
                    "A",
                    "B",
                ),
            ),
            "second": (
                make_swap_candidate(
                    third,
                    "C",
                    "D",
                ),
            ),
        }
    )

    optimizer = LocalSearchOptimizer(
        candidate_evaluator=evaluator,
        candidate_generator=generator,
        max_iterations=1,
    )

    result = optimizer.optimize(
        layout=initial,
        transition_statistics=None,
        character_statistics=None,
    )

    assert result.final_evaluation.layout == second
    assert result.final_score == 7.0
    assert result.iteration_count == 1

    assert result.steps[0].iteration == 1
    assert result.steps[0].move == SwapMove(
        first_letter="A",
        second_letter="B",
    )


def test_zero_max_iterations_returns_initial_evaluation():
    initial = make_layout("initial")
    better = make_layout("better")

    evaluator = FakeCandidateEvaluator(
        {
            "initial": 10.0,
            "better": 1.0,
        }
    )

    generator = FakeCandidateGenerator(
        {
            "initial": (
                make_swap_candidate(
                    better,
                    "A",
                    "B",
                ),
            ),
        }
    )

    optimizer = LocalSearchOptimizer(
        candidate_evaluator=evaluator,
        candidate_generator=generator,
        max_iterations=0,
    )

    result = optimizer.optimize(
        layout=initial,
        transition_statistics=None,
        character_statistics=None,
    )

    assert result.initial_evaluation.layout == initial
    assert result.final_evaluation.layout == initial
    assert result.steps == ()
    assert result.iteration_count == 0
    assert generator.generated_from == []


def test_negative_max_iterations_is_rejected():
    evaluator = FakeCandidateEvaluator({})

    try:
        LocalSearchOptimizer(
            candidate_evaluator=evaluator,
            max_iterations=-1,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_optimizer_generates_from_each_accepted_layout():
    initial = make_layout("initial")
    second = make_layout("second")
    third = make_layout("third")

    evaluator = FakeCandidateEvaluator(
        {
            "initial": 10.0,
            "second": 6.0,
            "third": 2.0,
        }
    )

    generator = FakeCandidateGenerator(
        {
            "initial": (
                make_swap_candidate(
                    second,
                    "A",
                    "B",
                ),
            ),
            "second": (
                make_swap_candidate(
                    third,
                    "C",
                    "D",
                ),
            ),
            "third": (),
        }
    )

    optimizer = LocalSearchOptimizer(
        candidate_evaluator=evaluator,
        candidate_generator=generator,
    )

    result = optimizer.optimize(
        layout=initial,
        transition_statistics=None,
        character_statistics=None,
    )

    assert generator.generated_from == [
        "initial",
        "second",
        "third",
    ]

    assert result.iteration_count == 2


def test_optimizer_records_accepted_steps():
    initial = make_layout("initial")
    second = make_layout("second")
    third = make_layout("third")

    evaluator = FakeCandidateEvaluator(
        {
            "initial": 10.0,
            "second": 7.0,
            "third": 3.0,
        }
    )

    generator = FakeCandidateGenerator(
        {
            "initial": (
                make_swap_candidate(
                    second,
                    "A",
                    "B",
                ),
            ),
            "second": (
                make_swap_candidate(
                    third,
                    "C",
                    "D",
                ),
            ),
            "third": (),
        }
    )

    optimizer = LocalSearchOptimizer(
        candidate_evaluator=evaluator,
        candidate_generator=generator,
    )

    result = optimizer.optimize(
        layout=initial,
        transition_statistics=None,
        character_statistics=None,
    )

    assert result.initial_score == 10.0
    assert result.final_score == 3.0
    assert result.improvement == 7.0

    assert len(result.steps) == 2

    assert result.steps[0].iteration == 1
    assert result.steps[0].move == SwapMove(
        first_letter="A",
        second_letter="B",
    )
    assert result.steps[0].score == 7.0
    assert result.steps[0].evaluation.layout == second

    assert result.steps[1].iteration == 2
    assert result.steps[1].move == SwapMove(
        first_letter="C",
        second_letter="D",
    )
    assert result.steps[1].score == 3.0
    assert result.steps[1].evaluation.layout == third