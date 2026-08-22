# tests/test_local_search_integration.py

from evaluator.candidate_evaluator import CandidateEvaluator
from evaluator.candidate_scorer import CandidateScorer
from evaluator.character_statistics import CharacterStatistics
from evaluator.constraint_set import ConstraintSet
from evaluator.finger_load_pipeline import FingerLoadPipeline
from evaluator.layout_evaluator import LayoutEvaluator
from evaluator.transition_statistics import TransitionStatistics
from models.candidate_score import CandidateScoreWeights
from models.enums import Finger, Hand
from models.finger_load_budget import FingerLoadBudget
from models.layout import Layout
from models.optimization_result import OptimizationResult
from models.transition_cost import TransitionCostWeights
from optimizer.local_search_optimizer import LocalSearchOptimizer
from optimizer.swap_candidate_generator import SwapCandidateGenerator


def make_layout() -> Layout:
    return Layout(
        name="Local Search Integration Test",
        version="0.1.0",
        layer="L0",
        description="Local search integration test layout",
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


def make_transition_statistics() -> TransitionStatistics:
    statistics = TransitionStatistics()

    statistics.add(
        {
            ("A", "B"): 100,
            ("A", "C"): 50,
            ("B", "A"): 80,
            ("C", "A"): 40,
        }
    )

    return statistics


def make_character_statistics() -> CharacterStatistics:
    statistics = CharacterStatistics()

    statistics.add(
        {
            "A": 70,
            "B": 30,
            "C": 20,
            "D": 10,
        }
    )

    return statistics


def make_transition_weights() -> TransitionCostWeights:
    return TransitionCostWeights(
        same_finger_penalty=10.0,
        same_hand_penalty=2.0,
        row_change_penalty=1.5,
        alternation_reward=2.0,
        inward_roll_reward=1.5,
        outward_roll_reward=0.5,
    )


def make_finger_load_budgets() -> tuple[
    FingerLoadBudget,
    ...,
]:
    return (
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            target_ratio=0.5,
        ),
        FingerLoadBudget(
            hand=Hand.RIGHT,
            finger=Finger.INDEX,
            target_ratio=0.5,
        ),
    )


def make_candidate_evaluator() -> CandidateEvaluator:
    return CandidateEvaluator(
        constraint_set=ConstraintSet([]),
        layout_evaluator=LayoutEvaluator(
            make_transition_weights()
        ),
        finger_load_pipeline=FingerLoadPipeline(),
        candidate_scorer=CandidateScorer(
            CandidateScoreWeights(
                transition_weight=1.0,
                finger_load_weight=1.0,
            )
        ),
        finger_load_budgets=make_finger_load_budgets(),
    )


def test_local_search_with_real_components():
    layout = make_layout()
    transition_statistics = make_transition_statistics()
    character_statistics = make_character_statistics()

    evaluator = make_candidate_evaluator()

    initial_evaluation = evaluator.evaluate(
        layout,
        transition_statistics,
        character_statistics,
    )

    optimizer = LocalSearchOptimizer(
        candidate_evaluator=evaluator,
        candidate_generator=SwapCandidateGenerator(),
        max_iterations=3,
    )

    result = optimizer.optimize(
        layout,
        transition_statistics,
        character_statistics,
    )

    assert isinstance(result, OptimizationResult)

    assert initial_evaluation.is_valid is True
    assert initial_evaluation.score is not None

    assert result.final_evaluation.is_valid is True
    assert result.final_score is not None

    assert result.final_score <= initial_evaluation.score


def test_local_search_preserves_valid_layout():
    layout = make_layout()

    optimizer = LocalSearchOptimizer(
        candidate_evaluator=make_candidate_evaluator(),
        candidate_generator=SwapCandidateGenerator(),
        max_iterations=2,
    )

    result = optimizer.optimize(
        layout,
        make_transition_statistics(),
        make_character_statistics(),
    )

    final = result.final_evaluation

    assert final.is_valid is True
    assert final.layout is not None
    assert len(final.layout.mapping) == 26
    assert set(final.layout.mapping) == set(layout.mapping)


def test_local_search_does_not_worsen_score():
    layout = make_layout()
    transition_statistics = make_transition_statistics()
    character_statistics = make_character_statistics()

    evaluator = make_candidate_evaluator()

    initial = evaluator.evaluate(
        layout,
        transition_statistics,
        character_statistics,
    )

    optimizer = LocalSearchOptimizer(
        candidate_evaluator=evaluator,
        candidate_generator=SwapCandidateGenerator(),
        max_iterations=5,
    )

    result = optimizer.optimize(
        layout,
        transition_statistics,
        character_statistics,
    )

    assert initial.score is not None
    assert result.final_score is not None

    assert result.final_score <= initial.score


def test_local_search_records_consistent_history():
    layout = make_layout()

    optimizer = LocalSearchOptimizer(
        candidate_evaluator=make_candidate_evaluator(),
        candidate_generator=SwapCandidateGenerator(),
        max_iterations=3,
    )

    result = optimizer.optimize(
        layout,
        make_transition_statistics(),
        make_character_statistics(),
    )

    assert result.iteration_count == len(result.steps)

    if result.steps:
        assert (
            result.final_evaluation
            == result.steps[-1].evaluation
        )

        assert (
            result.final_score
            == result.steps[-1].score
        )

        scores = tuple(
            step.score
            for step in result.steps
        )

        assert all(
            score is not None
            for score in scores
        )

        assert all(
            current < previous
            for previous, current in zip(
                (
                    result.initial_score,
                    *scores[:-1],
                ),
                scores,
            )
        )
    else:
        assert (
            result.final_evaluation
            == result.initial_evaluation
        )


def test_local_search_records_real_swap_moves():
    layout = make_layout()

    optimizer = LocalSearchOptimizer(
        candidate_evaluator=make_candidate_evaluator(),
        candidate_generator=SwapCandidateGenerator(),
        max_iterations=3,
    )

    result = optimizer.optimize(
        layout,
        make_transition_statistics(),
        make_character_statistics(),
    )

    for step in result.steps:
        assert (
            step.move.first_letter
            != step.move.second_letter
        )

        assert step.move.first_letter in layout.mapping
        assert step.move.second_letter in layout.mapping