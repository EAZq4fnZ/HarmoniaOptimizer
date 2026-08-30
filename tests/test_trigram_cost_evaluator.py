# tests/test_trigram_cost_evaluator.py

import pytest

from evaluator.trigram_cost_evaluator import TrigramCostEvaluator
from models.enums import Finger, Hand, Layer, RollDirection, Row
from models.logical_key import LogicalKey
from models.logical_position import LogicalPosition
from models.trigram_cost import TrigramCost, TrigramCostWeights
from models.trigram_features import TrigramFeatures


def make_key(
    key_id: str,
    *,
    hand: Hand = Hand.LEFT,
    finger: Finger = Finger.MIDDLE,
    column: int = 1,
) -> LogicalKey:
    return LogicalKey(
        id=key_id,
        position=LogicalPosition(
            layer=Layer.L0,
            hand=hand,
            finger=finger,
            row=Row.HOME,
            column=column,
        ),
    )


def make_features(
    *,
    same_finger_skip: bool = False,
    alternating_hands: bool = False,
    same_hand: bool = False,
    roll_direction: RollDirection = RollDirection.NONE,
    redirect: bool = False,
) -> TrigramFeatures:
    return TrigramFeatures(
        first=make_key(
            "A",
            column=1,
        ),
        second=make_key(
            "B",
            column=2,
        ),
        third=make_key(
            "C",
            column=3,
        ),
        same_finger_skip=same_finger_skip,
        same_hand_same_finger_skip=(
            same_finger_skip and same_hand
        ),
        alternating_same_finger_skip=(
            same_finger_skip and alternating_hands
        ),
        alternating_hands=alternating_hands,
        same_hand=same_hand,
        roll_direction=roll_direction,
        redirect=redirect,
    )


def make_weights() -> TrigramCostWeights:
    return TrigramCostWeights(
        same_finger_skip_penalty=8.0,
        redirect_penalty=4.0,
        alternation_reward=2.0,
        inward_roll_reward=1.5,
        outward_roll_reward=0.5,
    )


def test_returns_trigram_cost() -> None:
    evaluator = TrigramCostEvaluator(
        make_weights()
    )

    cost = evaluator.evaluate(
        make_features()
    )

    assert isinstance(
        cost,
        TrigramCost,
    )


def test_no_features_have_zero_cost() -> None:
    evaluator = TrigramCostEvaluator(
        make_weights()
    )

    cost = evaluator.evaluate(
        make_features()
    )

    assert cost.total == pytest.approx(0.0)


def test_same_hand_same_finger_skip_penalty() -> None:
    evaluator = TrigramCostEvaluator(
        make_weights()
    )

    cost = evaluator.evaluate(
        make_features(
            same_finger_skip=True,
            same_hand=True,
        )
    )

    assert cost.same_finger_skip == pytest.approx(8.0)
    assert cost.total == pytest.approx(8.0)


def test_redirect_penalty() -> None:
    evaluator = TrigramCostEvaluator(
        make_weights()
    )

    cost = evaluator.evaluate(
        make_features(
            same_hand=True,
            redirect=True,
        )
    )

    assert cost.redirect == pytest.approx(4.0)
    assert cost.total == pytest.approx(4.0)


def test_same_finger_skip_suppresses_redirect_penalty() -> None:
    evaluator = TrigramCostEvaluator(
        make_weights()
    )

    cost = evaluator.evaluate(
        make_features(
            same_finger_skip=True,
            same_hand=True,
            redirect=True,
        )
    )

    assert cost.same_finger_skip == pytest.approx(8.0)
    assert cost.redirect == pytest.approx(0.0)
    assert cost.total == pytest.approx(8.0)


def test_alternation_is_reward() -> None:
    evaluator = TrigramCostEvaluator(
        make_weights()
    )

    cost = evaluator.evaluate(
        make_features(
            alternating_hands=True,
        )
    )

    assert cost.alternation == pytest.approx(-2.0)
    assert cost.total == pytest.approx(-2.0)


def test_inward_roll_is_reward() -> None:
    evaluator = TrigramCostEvaluator(
        make_weights()
    )

    cost = evaluator.evaluate(
        make_features(
            same_hand=True,
            roll_direction=RollDirection.INWARD,
        )
    )

    assert cost.inward_roll == pytest.approx(-1.5)
    assert cost.outward_roll == pytest.approx(0.0)
    assert cost.total == pytest.approx(-1.5)


def test_outward_roll_is_reward() -> None:
    evaluator = TrigramCostEvaluator(
        make_weights()
    )

    cost = evaluator.evaluate(
        make_features(
            same_hand=True,
            roll_direction=RollDirection.OUTWARD,
        )
    )

    assert cost.inward_roll == pytest.approx(0.0)
    assert cost.outward_roll == pytest.approx(-0.5)
    assert cost.total == pytest.approx(-0.5)


def test_cost_components_are_summed() -> None:
    cost = TrigramCost(
        same_finger_skip=8.0,
        redirect=0.0,
        alternation=-2.0,
        inward_roll=-1.5,
        outward_roll=0.0,
    )

    assert cost.total == pytest.approx(4.5)


def test_zero_weights_produce_zero_cost() -> None:
    evaluator = TrigramCostEvaluator(
        TrigramCostWeights()
    )

    cost = evaluator.evaluate(
        make_features(
            same_finger_skip=True,
            alternating_hands=True,
            same_hand=True,
            roll_direction=RollDirection.INWARD,
            redirect=True,
        )
    )

    assert cost.total == pytest.approx(0.0)


def test_weights_are_preserved() -> None:
    weights = make_weights()

    evaluator = TrigramCostEvaluator(
        weights
    )

    assert evaluator.weights is weights



def test_alternating_same_finger_skip_has_no_sfs_penalty() -> None:
    evaluator = TrigramCostEvaluator(
        make_weights()
    )

    cost = evaluator.evaluate(
        make_features(
            same_finger_skip=True,
            alternating_hands=True,
            same_hand=False,
        )
    )

    assert cost.same_finger_skip == pytest.approx(0.0)
    assert cost.alternation == pytest.approx(-2.0)
    assert cost.total == pytest.approx(-2.0)
