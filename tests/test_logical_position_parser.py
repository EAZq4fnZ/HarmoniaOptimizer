# tests/test_logical_position_parser.py

import pytest

from models.enums import Finger, Hand, Layer, Row
from models.logical_position import LogicalPosition
from models.logical_position_parser import LogicalPositionParser


def test_parse_logical_position():
    position = LogicalPositionParser.parse(
        "L-M-H-2"
    )

    assert position == LogicalPosition(
        layer=Layer.L0,
        hand=Hand.LEFT,
        finger=Finger.MIDDLE,
        row=Row.HOME,
        column=2,
    )


def test_parse_right_index_top():
    position = LogicalPositionParser.parse(
        "R-I-T-4"
    )

    assert position.hand is Hand.RIGHT
    assert position.finger is Finger.INDEX
    assert position.row is Row.TOP
    assert position.column == 4


def test_parse_bottom_row():
    position = LogicalPositionParser.parse(
        "L-R-B-1"
    )

    assert position.hand is Hand.LEFT
    assert position.finger is Finger.RING
    assert position.row is Row.BOTTOM
    assert position.column == 1


def test_parse_custom_layer():
    position = LogicalPositionParser.parse(
        "L-M-H-2",
        layer=Layer.L1,
    )

    assert position.layer is Layer.L1


def test_parser_is_case_insensitive():
    position = LogicalPositionParser.parse(
        "l-m-h-2"
    )

    assert position.hand is Hand.LEFT
    assert position.finger is Finger.MIDDLE
    assert position.row is Row.HOME


def test_parser_strips_whitespace():
    position = LogicalPositionParser.parse(
        "  L-M-H-2  "
    )

    assert position.column == 2


def test_invalid_number_of_parts():
    with pytest.raises(
        ValueError,
        match="HAND-FINGER-ROW-COLUMN",
    ):
        LogicalPositionParser.parse(
            "L-M-H"
        )


def test_unknown_hand():
    with pytest.raises(
        ValueError,
        match="Unknown hand code",
    ):
        LogicalPositionParser.parse(
            "X-M-H-2"
        )


def test_unknown_finger():
    with pytest.raises(
        ValueError,
        match="Unknown finger code",
    ):
        LogicalPositionParser.parse(
            "L-X-H-2"
        )


def test_unknown_row():
    with pytest.raises(
        ValueError,
        match="Unknown row code",
    ):
        LogicalPositionParser.parse(
            "L-M-X-2"
        )


def test_column_must_be_integer():
    with pytest.raises(
        ValueError,
        match="Column must be an integer",
    ):
        LogicalPositionParser.parse(
            "L-M-H-X"
        )


"""
def test_column_cannot_be_negative():
    with pytest.raises(
        ValueError,
        match="Column must be zero or greater",
    ):
        LogicalPositionParser.parse(
            "L-M-H--1"
        )
"""