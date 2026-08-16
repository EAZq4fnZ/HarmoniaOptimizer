# tests/test_logical_key.py
from models.enums import Finger, Hand, Layer, Row
from models.logical_key import LogicalKey
from models.logical_position import LogicalPosition


def make_position() -> LogicalPosition:
    return LogicalPosition(
        layer=Layer.L0,
        hand=Hand.LEFT,
        finger=Finger.MIDDLE,
        row=Row.HOME,
        column=2,
    )


def make_key() -> LogicalKey:
    return LogicalKey(
        id="A",
        position=make_position(),
    )


def test_logical_key_attributes():
    key = make_key()

    assert key.id == "A"
    assert key.position.layer is Layer.L0
    assert key.position.hand is Hand.LEFT
    assert key.position.finger is Finger.MIDDLE
    assert key.position.row is Row.HOME
    assert key.position.column == 2


def test_logical_key_is_immutable():
    key = make_key()

    try:
        key.id = "B"
    except AttributeError:
        pass
    else:
        raise AssertionError("LogicalKey should be immutable")


def test_logical_key_equality():
    key1 = make_key()
    key2 = make_key()

    assert key1 == key2


def test_different_logical_keys_are_not_equal():
    key1 = make_key()

    key2 = LogicalKey(
        id="B",
        position=make_position(),
    )

    assert key1 != key2


def test_logical_key_is_hashable():
    key = make_key()

    keys = {key}

    assert key in keys