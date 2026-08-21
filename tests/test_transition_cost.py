# tests/test_transition_cost.py

from evaluator.transition_cost import TransitionCostEvaluator
from models.enums import RollDirection
from models.transition import Transition
from models.transition_cost import TransitionCostWeights
from models.transition_evaluation import TransitionEvaluation
from models.transition_features import TransitionFeatures


def make_weights() -> TransitionCostWeights:
    return TransitionCostWeights(
        same_finger_penalty=10.0,
        same_hand_penalty=2.0,
        row_change_penalty=1.5,
        alternation_reward=2.0,
        inward_roll_reward=1.5,
        outward_roll_reward=0.5,
    )


def make_evaluation(
    *,
    is_alternating: bool = False,
    is_same_hand: bool = False,
    is_same_finger: bool = False,
    is_same_row: bool = True,
    roll_direction: RollDirection = RollDirection.NONE,
) -> TransitionEvaluation:
    transition = object.__new__(Transition)

    features = object.__new__(TransitionFeatures)

    return TransitionEvaluation(
        transition=transition,
        features=features,
        is_alternating=is_alternating,
        is_same_hand=is_same_hand,
        is_same_finger=is_same_finger,
        is_same_row=is_same_row,
        roll_direction=roll_direction,
    )


def test_same_finger_penalty():
    evaluator = TransitionCostEvaluator(
        make_weights()
    )

    evaluation = make_evaluation(
        is_same_hand=True,
        is_same_finger=True,
    )

    cost = evaluator.evaluate(evaluation)

    assert cost.same_finger == 10.0


def test_same_hand_penalty():
    evaluator = TransitionCostEvaluator(
        make_weights()
    )

    evaluation = make_evaluation(
        is_same_hand=True,
    )

    cost = evaluator.evaluate(evaluation)

    assert cost.same_hand == 2.0


def test_row_change_penalty():
    evaluator = TransitionCostEvaluator(
        make_weights()
    )

    evaluation = make_evaluation(
        is_same_row=False,
    )

    cost = evaluator.evaluate(evaluation)

    assert cost.row_change == 1.5


def test_alternation_reward():
    evaluator = TransitionCostEvaluator(
        make_weights()
    )

    evaluation = make_evaluation(
        is_alternating=True,
    )

    cost = evaluator.evaluate(evaluation)

    assert cost.alternation == -2.0


def test_inward_roll_reward():
    evaluator = TransitionCostEvaluator(
        make_weights()
    )

    evaluation = make_evaluation(
        roll_direction=RollDirection.INWARD,
    )

    cost = evaluator.evaluate(evaluation)

    assert cost.roll == -1.5


def test_outward_roll_reward():
    evaluator = TransitionCostEvaluator(
        make_weights()
    )

    evaluation = make_evaluation(
        roll_direction=RollDirection.OUTWARD,
    )

    cost = evaluator.evaluate(evaluation)

    assert cost.roll == -0.5


def test_non_roll_has_zero_roll_cost():
    evaluator = TransitionCostEvaluator(
        make_weights()
    )

    evaluation = make_evaluation(
        roll_direction=RollDirection.NONE,
    )

    cost = evaluator.evaluate(evaluation)

    assert cost.roll == 0.0


def test_total_cost():
    evaluator = TransitionCostEvaluator(
        make_weights()
    )

    evaluation = make_evaluation(
        is_same_hand=True,
        is_same_finger=True,
        is_same_row=False,
        roll_direction=RollDirection.NONE,
    )

    cost = evaluator.evaluate(evaluation)

    assert cost.total == 13.5


def test_alternating_inward_roll_total():
    evaluator = TransitionCostEvaluator(
        make_weights()
    )

    evaluation = make_evaluation(
        is_alternating=True,
        roll_direction=RollDirection.INWARD,
    )

    cost = evaluator.evaluate(evaluation)

    assert cost.total == -3.5