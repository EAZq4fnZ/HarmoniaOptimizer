# tests/test_transition.py
from models.enums import Finger, Hand, Layer, Row
from models.logical_key import LogicalKey
from models.logical_position import LogicalPosition
from models.transition import Transition


def make_source() -> LogicalKey:
    return LogicalKey(
        id="H",
        position=LogicalPosition(
            layer=Layer.L0,
            hand=Hand.LEFT,
            finger=Finger.RING,
            row=Row.HOME,
            column=1,
        ),
    )


def make_target() -> LogicalKey:
    return LogicalKey(
        id="E",
        position=LogicalPosition(
            layer=Layer.L0,
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            row=Row.HOME,
            column=2,
        ),
    )


def make_transition() -> Transition:
    return Transition(
        source=make_source(),
        target=make_target(),
    )


def test_transition_attributes():
    transition = make_transition()

    assert transition.source.id == "H"
    assert transition.target.id == "E"


def test_transition_source_position():
    transition = make_transition()

    assert transition.source.position.hand is Hand.LEFT
    assert transition.source.position.finger is Finger.RING
    assert transition.source.position.row is Row.HOME
    assert transition.source.position.column == 1


def test_transition_target_position():
    transition = make_transition()

    assert transition.target.position.hand is Hand.LEFT
    assert transition.target.position.finger is Finger.INDEX
    assert transition.target.position.row is Row.HOME
    assert transition.target.position.column == 2


def test_transition_is_immutable():
    transition = make_transition()

    try:
        transition.source = make_target()
    except AttributeError:
        pass
    else:
        raise AssertionError("Transition should be immutable")


def test_transition_equality():
    transition1 = make_transition()
    transition2 = make_transition()

    assert transition1 == transition2


def test_different_transitions_are_not_equal():
    transition1 = make_transition()

    transition2 = Transition(
        source=make_target(),
        target=make_source(),
    )

    assert transition1 != transition2


def test_transition_is_hashable():
    transition = make_transition()

    transitions = {transition}

    assert transition in transitions