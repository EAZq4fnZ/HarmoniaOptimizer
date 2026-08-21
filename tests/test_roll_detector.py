# tests/test_roll_detector.py

from evaluator.roll_detector import detect_roll_direction
from models.enums import Finger, Hand, Layer, RollDirection, Row
from models.logical_key import LogicalKey
from models.logical_position import LogicalPosition
from models.transition import Transition


def make_transition(
    *,
    hand: Hand,
    source_finger: Finger,
    target_finger: Finger,
    target_hand: Hand | None = None,
) -> Transition:
    if target_hand is None:
        target_hand = hand

    source = LogicalKey(
        id="A",
        position=LogicalPosition(
            layer=Layer.L0,
            hand=hand,
            finger=source_finger,
            row=Row.HOME,
            column=1,
        ),
    )

    target = LogicalKey(
        id="B",
        position=LogicalPosition(
            layer=Layer.L0,
            hand=target_hand,
            finger=target_finger,
            row=Row.HOME,
            column=2,
        ),
    )

    return Transition(
        source=source,
        target=target,
    )


def test_left_hand_inward_roll():
    transition = make_transition(
        hand=Hand.LEFT,
        source_finger=Finger.RING,
        target_finger=Finger.MIDDLE,
    )

    assert detect_roll_direction(transition) is RollDirection.INWARD


def test_left_hand_outward_roll():
    transition = make_transition(
        hand=Hand.LEFT,
        source_finger=Finger.MIDDLE,
        target_finger=Finger.RING,
    )

    assert detect_roll_direction(transition) is RollDirection.OUTWARD


def test_right_hand_inward_roll():
    transition = make_transition(
        hand=Hand.RIGHT,
        source_finger=Finger.MIDDLE,
        target_finger=Finger.RING,
    )

    assert detect_roll_direction(transition) is RollDirection.INWARD


def test_right_hand_outward_roll():
    transition = make_transition(
        hand=Hand.RIGHT,
        source_finger=Finger.RING,
        target_finger=Finger.MIDDLE,
    )

    assert detect_roll_direction(transition) is RollDirection.OUTWARD


def test_different_hands_are_not_roll():
    transition = make_transition(
        hand=Hand.LEFT,
        target_hand=Hand.RIGHT,
        source_finger=Finger.INDEX,
        target_finger=Finger.MIDDLE,
    )

    assert detect_roll_direction(transition) is RollDirection.NONE


def test_same_finger_is_not_roll():
    transition = make_transition(
        hand=Hand.LEFT,
        source_finger=Finger.INDEX,
        target_finger=Finger.INDEX,
    )

    assert detect_roll_direction(transition) is RollDirection.NONE


def test_skipped_finger_is_not_roll():
    transition = make_transition(
        hand=Hand.LEFT,
        source_finger=Finger.RING,
        target_finger=Finger.INDEX,
    )

    assert detect_roll_direction(transition) is RollDirection.NONE


def test_left_pinky_to_ring_is_inward():
    transition = make_transition(
        hand=Hand.LEFT,
        source_finger=Finger.PINKY,
        target_finger=Finger.RING,
    )

    assert detect_roll_direction(transition) is RollDirection.INWARD


def test_right_index_to_middle_is_inward():
    transition = make_transition(
        hand=Hand.RIGHT,
        source_finger=Finger.INDEX,
        target_finger=Finger.MIDDLE,
    )

    assert detect_roll_direction(transition) is RollDirection.INWARD