# tests/test_transition_evaluator.py

from evaluator.transition_evaluator import TransitionEvaluator
from models.enums import Finger, Hand, Layer, RollDirection, Row
from models.logical_key import LogicalKey
from models.logical_position import LogicalPosition
from models.transition import Transition
from models.transition_evaluation import TransitionEvaluation


def make_transition(
    source_hand: Hand = Hand.LEFT,
    target_hand: Hand = Hand.RIGHT,
    source_finger: Finger = Finger.INDEX,
    target_finger: Finger = Finger.MIDDLE,
    source_row: Row = Row.HOME,
    target_row: Row = Row.HOME,
) -> Transition:
    source = LogicalKey(
        id="A",
        position=LogicalPosition(
            layer=Layer.L0,
            hand=source_hand,
            finger=source_finger,
            row=source_row,
            column=1,
        ),
    )

    target = LogicalKey(
        id="B",
        position=LogicalPosition(
            layer=Layer.L0,
            hand=target_hand,
            finger=target_finger,
            row=target_row,
            column=2,
        ),
    )

    return Transition(
        source=source,
        target=target,
    )


def test_transition_evaluator_returns_evaluation():
    evaluator = TransitionEvaluator()
    transition = make_transition()

    evaluation = evaluator.evaluate(transition)

    assert isinstance(evaluation, TransitionEvaluation)


def test_transition_is_preserved():
    evaluator = TransitionEvaluator()
    transition = make_transition()

    evaluation = evaluator.evaluate(transition)

    assert evaluation.transition == transition


def test_features_are_preserved():
    evaluator = TransitionEvaluator()
    transition = make_transition()

    evaluation = evaluator.evaluate(transition)

    assert evaluation.features.transition == transition


def test_alternating_transition():
    evaluator = TransitionEvaluator()

    transition = make_transition(
        source_hand=Hand.LEFT,
        target_hand=Hand.RIGHT,
    )

    evaluation = evaluator.evaluate(transition)

    assert evaluation.is_alternating is True
    assert evaluation.is_same_hand is False


def test_same_hand_transition():
    evaluator = TransitionEvaluator()

    transition = make_transition(
        source_hand=Hand.LEFT,
        target_hand=Hand.LEFT,
    )

    evaluation = evaluator.evaluate(transition)

    assert evaluation.is_alternating is False
    assert evaluation.is_same_hand is True


def test_same_finger_transition():
    evaluator = TransitionEvaluator()

    transition = make_transition(
        source_hand=Hand.LEFT,
        target_hand=Hand.LEFT,
        source_finger=Finger.INDEX,
        target_finger=Finger.INDEX,
    )

    evaluation = evaluator.evaluate(transition)

    assert evaluation.is_same_finger is True


def test_same_finger_requires_same_hand():
    evaluator = TransitionEvaluator()

    transition = make_transition(
        source_hand=Hand.LEFT,
        target_hand=Hand.RIGHT,
        source_finger=Finger.INDEX,
        target_finger=Finger.INDEX,
    )

    evaluation = evaluator.evaluate(transition)

    assert evaluation.is_same_finger is False


def test_same_row_transition():
    evaluator = TransitionEvaluator()

    transition = make_transition(
        source_row=Row.HOME,
        target_row=Row.HOME,
    )

    evaluation = evaluator.evaluate(transition)

    assert evaluation.is_same_row is True


def test_different_row_transition():
    evaluator = TransitionEvaluator()

    transition = make_transition(
        source_row=Row.HOME,
        target_row=Row.TOP,
    )

    evaluation = evaluator.evaluate(transition)

    assert evaluation.is_same_row is False


def test_inward_roll_evaluation():
    evaluator = TransitionEvaluator()

    transition = make_transition(
        source_hand=Hand.LEFT,
        target_hand=Hand.LEFT,
        source_finger=Finger.RING,
        target_finger=Finger.MIDDLE,
    )

    evaluation = evaluator.evaluate(transition)

    assert evaluation.roll_direction is RollDirection.INWARD


def test_outward_roll_evaluation():
    evaluator = TransitionEvaluator()

    transition = make_transition(
        source_hand=Hand.LEFT,
        target_hand=Hand.LEFT,
        source_finger=Finger.MIDDLE,
        target_finger=Finger.RING,
    )

    evaluation = evaluator.evaluate(transition)

    assert evaluation.roll_direction is RollDirection.OUTWARD


def test_non_roll_evaluation():
    evaluator = TransitionEvaluator()

    transition = make_transition(
        source_hand=Hand.LEFT,
        target_hand=Hand.RIGHT,
        source_finger=Finger.INDEX,
        target_finger=Finger.MIDDLE,
    )

    evaluation = evaluator.evaluate(transition)

    assert evaluation.roll_direction is RollDirection.NONE