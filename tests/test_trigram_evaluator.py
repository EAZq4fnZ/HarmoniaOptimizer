# tests/test_trigram_evaluator.py

from evaluator.trigram_evaluator import TrigramEvaluator
from models.enums import Finger, Hand, Layer, RollDirection, Row
from models.logical_key import LogicalKey
from models.logical_position import LogicalPosition
from models.trigram_features import TrigramFeatures


def make_key(
    key_id: str,
    *,
    hand: Hand,
    finger: Finger,
    column: int,
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


def evaluate(
    first_hand: Hand,
    first_finger: Finger,
    second_hand: Hand,
    second_finger: Finger,
    third_hand: Hand,
    third_finger: Finger,
) -> TrigramFeatures:
    evaluator = TrigramEvaluator()

    return evaluator.evaluate(
        make_key(
            "A",
            hand=first_hand,
            finger=first_finger,
            column=1,
        ),
        make_key(
            "B",
            hand=second_hand,
            finger=second_finger,
            column=2,
        ),
        make_key(
            "C",
            hand=third_hand,
            finger=third_finger,
            column=3,
        ),
    )


def test_returns_trigram_features() -> None:
    features = evaluate(
        Hand.LEFT,
        Finger.RING,
        Hand.LEFT,
        Finger.MIDDLE,
        Hand.LEFT,
        Finger.INDEX,
    )

    assert isinstance(
        features,
        TrigramFeatures,
    )


def test_same_finger_skip() -> None:
    features = evaluate(
        Hand.LEFT,
        Finger.INDEX,
        Hand.LEFT,
        Finger.MIDDLE,
        Hand.LEFT,
        Finger.INDEX,
    )

    assert features.same_finger_skip is True


def test_same_finger_skip_requires_same_hand() -> None:
    features = evaluate(
        Hand.LEFT,
        Finger.INDEX,
        Hand.RIGHT,
        Finger.MIDDLE,
        Hand.RIGHT,
        Finger.INDEX,
    )

    assert features.same_finger_skip is False


def test_adjacent_same_finger_is_not_skip() -> None:
    features = evaluate(
        Hand.LEFT,
        Finger.INDEX,
        Hand.LEFT,
        Finger.INDEX,
        Hand.LEFT,
        Finger.MIDDLE,
    )

    assert features.same_finger_skip is False


def test_left_right_left_is_alternating() -> None:
    features = evaluate(
        Hand.LEFT,
        Finger.INDEX,
        Hand.RIGHT,
        Finger.INDEX,
        Hand.LEFT,
        Finger.MIDDLE,
    )

    assert features.alternating_hands is True
    assert features.same_hand is False


def test_right_left_right_is_alternating() -> None:
    features = evaluate(
        Hand.RIGHT,
        Finger.INDEX,
        Hand.LEFT,
        Finger.INDEX,
        Hand.RIGHT,
        Finger.MIDDLE,
    )

    assert features.alternating_hands is True
    assert features.same_hand is False


def test_left_hand_inward_roll() -> None:
    features = evaluate(
        Hand.LEFT,
        Finger.RING,
        Hand.LEFT,
        Finger.MIDDLE,
        Hand.LEFT,
        Finger.INDEX,
    )

    assert features.same_hand is True
    assert features.roll_direction is RollDirection.INWARD
    assert features.redirect is False


def test_left_hand_outward_roll() -> None:
    features = evaluate(
        Hand.LEFT,
        Finger.INDEX,
        Hand.LEFT,
        Finger.MIDDLE,
        Hand.LEFT,
        Finger.RING,
    )

    assert features.roll_direction is RollDirection.OUTWARD
    assert features.redirect is False


def test_right_hand_inward_roll() -> None:
    features = evaluate(
        Hand.RIGHT,
        Finger.INDEX,
        Hand.RIGHT,
        Finger.MIDDLE,
        Hand.RIGHT,
        Finger.RING,
    )

    assert features.roll_direction is RollDirection.INWARD
    assert features.redirect is False


def test_right_hand_outward_roll() -> None:
    features = evaluate(
        Hand.RIGHT,
        Finger.RING,
        Hand.RIGHT,
        Finger.MIDDLE,
        Hand.RIGHT,
        Finger.INDEX,
    )

    assert features.roll_direction is RollDirection.OUTWARD
    assert features.redirect is False


def test_left_hand_redirect() -> None:
    features = evaluate(
        Hand.LEFT,
        Finger.RING,
        Hand.LEFT,
        Finger.MIDDLE,
        Hand.LEFT,
        Finger.RING,
    )

    assert features.roll_direction is RollDirection.NONE
    assert features.redirect is True


def test_right_hand_redirect() -> None:
    features = evaluate(
        Hand.RIGHT,
        Finger.RING,
        Hand.RIGHT,
        Finger.MIDDLE,
        Hand.RIGHT,
        Finger.RING,
    )

    assert features.roll_direction is RollDirection.NONE
    assert features.redirect is True


def test_skipped_finger_is_not_three_key_roll() -> None:
    features = evaluate(
        Hand.LEFT,
        Finger.PINKY,
        Hand.LEFT,
        Finger.MIDDLE,
        Hand.LEFT,
        Finger.INDEX,
    )

    assert features.roll_direction is RollDirection.NONE
    assert features.redirect is False


def test_mixed_hand_sequence_is_not_roll() -> None:
    features = evaluate(
        Hand.LEFT,
        Finger.RING,
        Hand.RIGHT,
        Finger.MIDDLE,
        Hand.RIGHT,
        Finger.INDEX,
    )

    assert features.roll_direction is RollDirection.NONE
    assert features.redirect is False


def test_non_alternating_mixed_hands() -> None:
    features = evaluate(
        Hand.LEFT,
        Finger.RING,
        Hand.LEFT,
        Finger.MIDDLE,
        Hand.RIGHT,
        Finger.INDEX,
    )

    assert features.alternating_hands is False
    assert features.same_hand is False
