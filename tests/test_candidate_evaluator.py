# tests/test_candidate_evaluator.py

from evaluator.candidate_evaluator import CandidateEvaluator
from evaluator.candidate_scorer import CandidateScorer
from evaluator.constraint_set import ConstraintSet
from evaluator.forbidden_position_constraint import (
    ForbiddenPositionConstraint,
)
from evaluator.layout_evaluator import LayoutEvaluator
from evaluator.transition_statistics import TransitionStatistics
from models.candidate_score import CandidateScoreWeights
from models.layout import Layout
from models.transition_cost import TransitionCostWeights


def make_layout() -> Layout:
    return Layout(
        name="Candidate Test Layout",
        version="0.1.0",
        layer="L0",
        description="Candidate evaluator test layout",
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


def make_weights() -> TransitionCostWeights:
    return TransitionCostWeights(
        same_finger_penalty=10.0,
        same_hand_penalty=2.0,
        row_change_penalty=1.5,
        alternation_reward=2.0,
        inward_roll_reward=1.5,
        outward_roll_reward=0.5,
    )


def make_statistics() -> TransitionStatistics:
    statistics = TransitionStatistics()

    statistics.add(
        {
            ("A", "B"): 1,
        }
    )

    return statistics


def make_candidate_evaluator(
    constraint_set: ConstraintSet,
) -> CandidateEvaluator:
    layout_evaluator = LayoutEvaluator(
        make_weights()
    )

    candidate_scorer = CandidateScorer(
        CandidateScoreWeights(
            transition_weight=1.0,
            finger_load_weight=1.0,
        )
    )

    return CandidateEvaluator(
        constraint_set=constraint_set,
        layout_evaluator=layout_evaluator,
        candidate_scorer=candidate_scorer,
    )


def test_valid_candidate_is_valid():
    evaluator = make_candidate_evaluator(
        ConstraintSet([])
    )

    result = evaluator.evaluate(
        make_layout(),
        make_statistics(),
    )

    assert result.is_valid is True


def test_valid_candidate_has_layout_evaluation():
    evaluator = make_candidate_evaluator(
        ConstraintSet([])
    )

    result = evaluator.evaluate(
        make_layout(),
        make_statistics(),
    )

    assert result.layout_evaluation is not None


def test_valid_candidate_has_score():
    evaluator = make_candidate_evaluator(
        ConstraintSet([])
    )

    result = evaluator.evaluate(
        make_layout(),
        make_statistics(),
    )

    # A -> B uses alternating hands and the same row.
    assert result.score == -2.0


def test_valid_candidate_has_candidate_score():
    evaluator = make_candidate_evaluator(
        ConstraintSet([])
    )

    result = evaluator.evaluate(
        make_layout(),
        make_statistics(),
    )

    assert result.candidate_score is not None
    assert result.candidate_score.transition_score == -2.0
    assert result.candidate_score.finger_load_score == 0.0


def test_candidate_preserves_layout():
    layout = make_layout()

    evaluator = make_candidate_evaluator(
        ConstraintSet([])
    )

    result = evaluator.evaluate(
        layout,
        make_statistics(),
    )

    assert result.layout == layout


def test_invalid_candidate_is_rejected():
    constraint = ForbiddenPositionConstraint(
        frozenset({
            "L-I-H-3",
        })
    )

    evaluator = make_candidate_evaluator(
        ConstraintSet([constraint])
    )

    result = evaluator.evaluate(
        make_layout(),
        make_statistics(),
    )

    assert result.is_valid is False
    assert result.constraint_evaluation.violation_count == 1


def test_invalid_candidate_has_no_layout_evaluation():
    constraint = ForbiddenPositionConstraint(
        frozenset({
            "L-I-H-3",
        })
    )

    evaluator = make_candidate_evaluator(
        ConstraintSet([constraint])
    )

    result = evaluator.evaluate(
        make_layout(),
        make_statistics(),
    )

    assert result.layout_evaluation is None


def test_invalid_candidate_has_no_score():
    constraint = ForbiddenPositionConstraint(
        frozenset({
            "L-I-H-3",
        })
    )

    evaluator = make_candidate_evaluator(
        ConstraintSet([constraint])
    )

    result = evaluator.evaluate(
        make_layout(),
        make_statistics(),
    )

    assert result.candidate_score is None
    assert result.score is None