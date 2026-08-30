# tests/test_candidate_evaluator.py

import pytest

from evaluator.candidate_evaluator import CandidateEvaluator
from evaluator.candidate_scorer import CandidateScorer
from evaluator.character_statistics import CharacterStatistics
from evaluator.constraint_set import ConstraintSet
from evaluator.finger_load_pipeline import FingerLoadPipeline
from evaluator.forbidden_position_constraint import (
    ForbiddenPositionConstraint,
)
from evaluator.layout_evaluator import LayoutEvaluator
from evaluator.transition_statistics import TransitionStatistics
from evaluator.trigram_layout_evaluator import (
    TrigramLayoutEvaluator,
)
from evaluator.trigram_statistics import TrigramStatistics
from models.candidate_score import CandidateScoreWeights
from models.enums import Finger, Hand
from models.finger_load_budget import FingerLoadBudget
from models.layout import Layout
from models.transition_cost import TransitionCostWeights
from models.trigram_cost import TrigramCostWeights


def make_trigram_candidate_evaluator(
    constraint_set: ConstraintSet,
    *,
    trigram_weight: float = 1.0,
) -> CandidateEvaluator:
    layout_evaluator = LayoutEvaluator(
        make_transition_weights()
    )

    trigram_layout_evaluator = (
        TrigramLayoutEvaluator(
            make_trigram_weights()
        )
    )

    finger_load_pipeline = FingerLoadPipeline()

    candidate_scorer = CandidateScorer(
        CandidateScoreWeights(
            transition_weight=1.0,
            trigram_weight=trigram_weight,
            finger_load_weight=1.0,
        )
    )

    return CandidateEvaluator(
        constraint_set=constraint_set,
        layout_evaluator=layout_evaluator,
        finger_load_pipeline=finger_load_pipeline,
        candidate_scorer=candidate_scorer,
        finger_load_budgets=make_finger_load_budgets(),
        trigram_layout_evaluator=(
            trigram_layout_evaluator
        ),
    )

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


def make_transition_weights() -> TransitionCostWeights:
    return TransitionCostWeights(
        same_finger_penalty=10.0,
        same_hand_penalty=2.0,
        row_change_penalty=1.5,
        alternation_reward=2.0,
        inward_roll_reward=1.5,
        outward_roll_reward=0.5,
    )


def make_transition_statistics() -> TransitionStatistics:
    statistics = TransitionStatistics()

    statistics.add(
        {
            ("A", "B"): 1,
        }
    )

    return statistics

def make_trigram_weights() -> TrigramCostWeights:
    return TrigramCostWeights(
        same_finger_skip_penalty=8.0,
        redirect_penalty=4.0,
        alternation_reward=2.0,
        inward_roll_reward=1.5,
        outward_roll_reward=0.5,
    )


def make_trigram_statistics() -> TrigramStatistics:
    statistics = TrigramStatistics()

    statistics.record(
        "A",
        "B",
        "A",
        weight=10.0,
    )

    return statistics

def make_character_statistics() -> CharacterStatistics:
    statistics = CharacterStatistics()

    statistics.add(
        {
            "A": 70,
            "B": 30,
        }
    )

    return statistics


def make_finger_load_budgets() -> tuple[
    FingerLoadBudget,
    ...
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


def make_candidate_evaluator(
    constraint_set: ConstraintSet,
) -> CandidateEvaluator:
    layout_evaluator = LayoutEvaluator(
        make_transition_weights()
    )

    finger_load_pipeline = FingerLoadPipeline()

    candidate_scorer = CandidateScorer(
        CandidateScoreWeights(
            transition_weight=1.0,
            finger_load_weight=1.0,
        )
    )

    return CandidateEvaluator(
        constraint_set=constraint_set,
        layout_evaluator=layout_evaluator,
        finger_load_pipeline=finger_load_pipeline,
        candidate_scorer=candidate_scorer,
        finger_load_budgets=make_finger_load_budgets(),
    )


def evaluate_valid_candidate():
    evaluator = make_candidate_evaluator(
        ConstraintSet([])
    )

    return evaluator.evaluate(
        make_layout(),
        make_transition_statistics(),
        make_character_statistics(),
    )


def test_valid_candidate_is_valid():
    result = evaluate_valid_candidate()

    assert result.is_valid is True


def test_valid_candidate_has_layout_evaluation():
    result = evaluate_valid_candidate()

    assert result.layout_evaluation is not None


def test_valid_candidate_has_candidate_score():
    result = evaluate_valid_candidate()

    assert result.candidate_score is not None


def test_transition_score_is_included():
    result = evaluate_valid_candidate()

    assert result.candidate_score is not None

    # A -> B:
    # alternating hands, same row
    # normalized transition score = -2.0
    assert result.candidate_score.transition_score == pytest.approx(
        -2.0
    )


def test_finger_load_score_is_included():
    result = evaluate_valid_candidate()

    assert result.candidate_score is not None

    # A = left index = 70%
    # target = 50%
    # excess = 20%
    #
    # B = right index = 30%
    # target = 50%
    # excess = 0%
    #
    # total finger-load penalty = 0.2
    assert result.candidate_score.finger_load_score == pytest.approx(
        0.2
    )


def test_combined_candidate_score():
    result = evaluate_valid_candidate()

    # transition = -2.0
    # finger load = +0.2
    #
    # final = -1.8
    assert result.score == pytest.approx(-1.8)


def test_candidate_preserves_layout():
    layout = make_layout()

    evaluator = make_candidate_evaluator(
        ConstraintSet([])
    )

    result = evaluator.evaluate(
        layout,
        make_transition_statistics(),
        make_character_statistics(),
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
        make_transition_statistics(),
        make_character_statistics(),
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
        make_transition_statistics(),
        make_character_statistics(),
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
        make_transition_statistics(),
        make_character_statistics(),
    )

    assert result.candidate_score is None
    assert result.score is None

def test_candidate_evaluator_includes_trigram_score():
    evaluator = make_trigram_candidate_evaluator(
        ConstraintSet([]),
        trigram_weight=1.0,
    )

    result = evaluator.evaluate(
        make_layout(),
        make_transition_statistics(),
        make_character_statistics(),
        trigram_statistics=(
            make_trigram_statistics()
        ),
    )

    assert result.candidate_score is not None

    # A -> B -> A:
    #
    # A = left index
    # B = right index
    # A = left index
    #
    # Alternating hands:
    # alternation reward = -2.0
    #
    # Same finger skip is alternating-hand,
    # so no same-hand SFS penalty applies.
    assert (
        result.candidate_score.trigram_score
        == pytest.approx(-2.0)
    )


def test_candidate_evaluator_applies_trigram_weight():
    evaluator = make_trigram_candidate_evaluator(
        ConstraintSet([]),
        trigram_weight=2.0,
    )

    result = evaluator.evaluate(
        make_layout(),
        make_transition_statistics(),
        make_character_statistics(),
        trigram_statistics=(
            make_trigram_statistics()
        ),
    )

    assert result.candidate_score is not None

    # Existing:
    # transition = -2.0
    # finger load = +0.2
    #
    # Trigram:
    # normalized score = -2.0
    # weight = 2.0
    # contribution = -4.0
    #
    # total = -2.0 + 0.2 - 4.0 = -5.8
    assert result.score == pytest.approx(
        -5.8
    )


def test_zero_trigram_weight_preserves_candidate_score():
    evaluator = make_trigram_candidate_evaluator(
        ConstraintSet([]),
        trigram_weight=0.0,
    )

    result = evaluator.evaluate(
        make_layout(),
        make_transition_statistics(),
        make_character_statistics(),
        trigram_statistics=(
            make_trigram_statistics()
        ),
    )

    assert result.candidate_score is not None

    assert (
        result.candidate_score.trigram_score
        == pytest.approx(-2.0)
    )

    # Same result as the original transition +
    # finger-load scoring path.
    assert result.score == pytest.approx(
        -1.8
    )