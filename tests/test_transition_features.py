# tests/test_transition_features.py

from models.logical_key import LogicalKey
from models.transition import Transition
from models.transition_features import TransitionFeatures
from evaluator.transition_features import extract_transition_features


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
        hand=source_hand,
        finger=source_finger,
        row=source_row,
        column="1",
    )

    target = LogicalKey(
        id="B",
        hand=target_hand,
        finger=target_finger,
        row=target_row,
        column="2",
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
        source_finger="index",
        target_finger="index",
    )

    features = extract_transition_features(transition)

    assert features.same_finger is True


def test_different_fingers():
    transition = make_transition(
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
        target_row="upper",
    )

    features = extract_transition_features(transition)

    assert features.same_row is False


def test_transition_is_preserved():
    transition = make_transition()

    features = extract_transition_features(transition)

    assert features.transition == transition
