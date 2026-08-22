# tests/test_optimization_config.py

import pytest

from models.candidate_score import CandidateScoreWeights
from models.enums import Finger, Hand
from models.finger_load_budget import FingerLoadBudget
from models.optimization_config import OptimizationConfig
from models.transition_cost import TransitionCostWeights


def make_transition_weights() -> TransitionCostWeights:
    return TransitionCostWeights(
        same_finger_penalty=10.0,
        same_hand_penalty=2.0,
        row_change_penalty=1.5,
        alternation_reward=2.0,
        inward_roll_reward=1.5,
        outward_roll_reward=0.5,
    )


def make_candidate_weights() -> CandidateScoreWeights:
    return CandidateScoreWeights(
        transition_weight=1.0,
        finger_load_weight=1.0,
    )


def make_budgets() -> tuple[
    FingerLoadBudget,
    ...,
]:
    return (
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            target_ratio=0.25,
            tolerance=0.05,
        ),
        FingerLoadBudget(
            hand=Hand.RIGHT,
            finger=Finger.INDEX,
            target_ratio=0.25,
            tolerance=0.05,
        ),
    )


def make_config() -> OptimizationConfig:
    return OptimizationConfig(
        version="1.0",
        transition_cost_weights=make_transition_weights(),
        candidate_score_weights=make_candidate_weights(),
        finger_load_budgets=make_budgets(),
    )


def test_optimization_config_attributes():
    transition_weights = make_transition_weights()
    candidate_weights = make_candidate_weights()
    budgets = make_budgets()

    config = OptimizationConfig(
        version="1.0",
        transition_cost_weights=transition_weights,
        candidate_score_weights=candidate_weights,
        finger_load_budgets=budgets,
    )

    assert config.version == "1.0"
    assert (
        config.transition_cost_weights
        == transition_weights
    )
    assert (
        config.candidate_score_weights
        == candidate_weights
    )
    assert config.finger_load_budgets == budgets


def test_transition_weights_are_preserved():
    config = make_config()

    weights = config.transition_cost_weights

    assert weights.same_finger_penalty == 10.0
    assert weights.same_hand_penalty == 2.0
    assert weights.row_change_penalty == 1.5
    assert weights.alternation_reward == 2.0
    assert weights.inward_roll_reward == 1.5
    assert weights.outward_roll_reward == 0.5


def test_candidate_weights_are_preserved():
    config = make_config()

    weights = config.candidate_score_weights

    assert weights.transition_weight == 1.0
    assert weights.finger_load_weight == 1.0


def test_finger_load_budgets_are_preserved():
    config = make_config()

    assert len(config.finger_load_budgets) == 2

    assert (
        config.finger_load_budgets[0].hand
        == Hand.LEFT
    )

    assert (
        config.finger_load_budgets[0].finger
        == Finger.INDEX
    )


def test_empty_version_is_rejected():
    with pytest.raises(
        ValueError,
        match="version",
    ):
        OptimizationConfig(
            version="",
            transition_cost_weights=make_transition_weights(),
            candidate_score_weights=make_candidate_weights(),
            finger_load_budgets=make_budgets(),
        )


def test_whitespace_version_is_rejected():
    with pytest.raises(
        ValueError,
        match="version",
    ):
        OptimizationConfig(
            version="   ",
            transition_cost_weights=make_transition_weights(),
            candidate_score_weights=make_candidate_weights(),
            finger_load_budgets=make_budgets(),
        )


def test_empty_finger_load_budgets_are_rejected():
    with pytest.raises(
        ValueError,
        match="finger_load_budgets",
    ):
        OptimizationConfig(
            version="1.0",
            transition_cost_weights=make_transition_weights(),
            candidate_score_weights=make_candidate_weights(),
            finger_load_budgets=(),
        )


def test_optimization_config_is_immutable():
    config = make_config()

    with pytest.raises(AttributeError):
        config.version = "2.0"