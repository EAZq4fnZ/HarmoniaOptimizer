# tests/test_logical_position_factory.py
from models.enums import Finger, Hand, Layer, Row
from models.logical_position import LogicalPosition
from models.logical_position_factory import LogicalPositionFactory


def test_create_logical_position():
    position = LogicalPositionFactory.create(
        layer=Layer.L0,
        hand=Hand.LEFT,
        finger=Finger.MIDDLE,
        row=Row.HOME,
        column=2,
    )

    assert position == LogicalPosition(
        layer=Layer.L0,
        hand=Hand.LEFT,
        finger=Finger.MIDDLE,
        row=Row.HOME,
        column=2,
    )