# tests/test_logical_position.py
from models.enums import Finger, Hand, Layer, Row
from models.logical_position import LogicalPosition


def make_position() -> LogicalPosition:
    return LogicalPosition(
        layer=Layer.L0,
        hand=Hand.LEFT,
        finger=Finger.MIDDLE,
        row=Row.HOME,
        column=2,
    )


def test_logical_position_attributes():
    position = make_position()

    assert position.layer is Layer.L0
    assert position.hand is Hand.LEFT
    assert position.finger is Finger.MIDDLE
    assert position.row is Row.HOME
    assert position.column == 2


def test_logical_position_is_immutable():
    position = make_position()

    try:
        position.column = 3
    except AttributeError:
        pass
    else:
        raise AssertionError("LogicalPosition should be immutable")


def test_logical_position_equality():
    position1 = make_position()
    position2 = make_position()

    assert position1 == position2


def test_different_logical_positions_are_not_equal():
    position1 = make_position()

    position2 = LogicalPosition(
        layer=Layer.L0,
        hand=Hand.LEFT,
        finger=Finger.MIDDLE,
        row=Row.TOP,
        column=2,
    )

    assert position1 != position2


def test_logical_position_is_hashable():
    position = make_position()

    positions = {position}

    assert position in positions