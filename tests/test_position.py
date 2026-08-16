# tests/test_position.py
from models.position import Position


def make_position() -> Position:
    return Position(
        x=1.0,
        y=2.0,
        z=3.0,
    )


def test_position_attributes():
    position = make_position()

    assert position.x == 1.0
    assert position.y == 2.0
    assert position.z == 3.0


def test_position_is_immutable():
    position = make_position()

    try:
        position.x = 4.0
    except AttributeError:
        pass
    else:
        raise AssertionError("Position should be immutable")


def test_position_equality():
    position1 = make_position()
    position2 = make_position()

    assert position1 == position2


def test_different_positions_are_not_equal():
    position1 = make_position()

    position2 = Position(
        x=2.0,
        y=2.0,
        z=3.0,
    )

    assert position1 != position2


def test_position_is_hashable():
    position = make_position()

    positions = {position}

    assert position in positions