# tests/test_transition_features.py

from evaluator.transition_features import extract_transition_features
from models.enums import Finger, Hand, Layer, RollDirection, Row
from models.logical_key import LogicalKey
from models.logical_position import LogicalPosition
from models.transition import Transition
from models.transition_features import TransitionFeatures


def make_transition(
    source_hand: str = "left",
    target_hand: str = "right",
    source_finger: str = "index",
    target_finger: str = "middle",
    source_row: str = "home",
    target_row: str = "home",
) -> Transition:

    source = LogicalKey(
        id="A",
        position=LogicalPosition(
            layer=Layer.L0,
            hand=Hand(source_hand),
            finger=Finger(source_finger),
            row=Row(source_row),
            column=1,
        ),
    )

    target = LogicalKey(
        id="B",
        position=LogicalPosition(
            layer=Layer.L0,
            hand=Hand(target_hand),
            finger=Finger(target_finger),
            row=Row(target_row),
            column=2,
        ),
    )

    return Transition(
        source=source,
        target=target,
    )


def test_transition_features_type():
    transition = make_transition()

    features = extract_transition_features(transition)

    assert isinstance(features, TransitionFeatures)


def test_alternating_hands():
    transition = make_transition(
        source_hand="left",
        target_hand="right",
    )

    features = extract_transition_features(transition)

    assert features.alternating_hands is True
    assert features.same_hand is False


def test_same_hand():
    transition = make_transition(
        source_hand="left",
        target_hand="left",
    )

    features = extract_transition_features(transition)

    assert features.alternating_hands is False
    assert features.same_hand is True


def test_same_finger():
    transition = make_transition(
        source_hand="left",
        target_hand="left",
        source_finger="index",
        target_finger="index",
    )

    features = extract_transition_features(transition)

    assert features.same_finger is True


def test_different_fingers():
    transition = make_transition(
        source_hand="left",
        target_hand="left",
        source_finger="index",
        target_finger="middle",
    )

    features = extract_transition_features(transition)

    assert features.same_finger is False


def test_same_row():
    transition = make_transition(
        source_row="home",
        target_row="home",
    )

    features = extract_transition_features(transition)

    assert features.same_row is True


def test_different_rows():
    transition = make_transition(
        source_row="home",
        target_row="top",
    )

    features = extract_transition_features(transition)

    assert features.same_row is False


def test_transition_is_preserved():
    transition = make_transition()

    features = extract_transition_features(transition)

    assert features.transition == transition


def test_same_finger_requires_same_hand():
    transition = make_transition(
        source_hand="left",
        target_hand="right",
        source_finger="index",
        target_finger="index",
    )

    features = extract_transition_features(transition)

    assert features.same_finger is False


def test_inward_roll_direction():
    transition = make_transition(
        source_hand="left",
        target_hand="left",
        source_finger="ring",
        target_finger="middle",
    )

    features = extract_transition_features(transition)

    assert features.roll_direction is RollDirection.INWARD


def test_outward_roll_direction():
    transition = make_transition(
        source_hand="left",
        target_hand="left",
        source_finger="middle",
        target_finger="ring",
    )

    features = extract_transition_features(transition)

    assert features.roll_direction is RollDirection.OUTWARD


def test_alternating_hands_have_no_roll():
    transition = make_transition(
        source_hand="left",
        target_hand="right",
        source_finger="index",
        target_finger="middle",
    )

    features = extract_transition_features(transition)

    assert features.roll_direction is RollDirection.NONE