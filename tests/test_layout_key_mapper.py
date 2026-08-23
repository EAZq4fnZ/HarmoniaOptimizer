# tests/test_layout_key_mapper.py

import string

import pytest

from models.enums import Finger, Hand, Layer, Row
from models.layout import Layout
from models.layout_key_mapper import LayoutKeyMapper
from models.logical_key import LogicalKey


def make_layout(
    *,
    layer: str = "L0",
) -> Layout:
    position_ids = []

    for hand in ("L", "R"):
        for finger in ("P", "R", "M", "I"):
            for row in ("T", "H", "B"):
                position_ids.append(
                    f"{hand}-{finger}-{row}-1"
                )

    # 4 fingers × 3 rows × 2 hands = 24 positions.
    # Add two extra logical columns to reach 26.
    position_ids.extend(
        (
            "L-I-H-2",
            "R-I-H-2",
        )
    )

    mapping = dict(
        zip(
            string.ascii_uppercase,
            position_ids,
            strict=True,
        )
    )

    return Layout(
        name="Mapper Test Layout",
        version="0.1.0",
        layer=layer,
        description="LayoutKeyMapper test",
        mapping=mapping,
    )


def test_mapper_returns_logical_key():
    mapper = LayoutKeyMapper(
        make_layout()
    )

    key = mapper.key("A")

    assert isinstance(key, LogicalKey)
    assert key.id == "A"


def test_mapper_parses_logical_position():
    mapper = LayoutKeyMapper(
        make_layout()
    )

    key = mapper.key("A")

    assert key.position.layer is Layer.L0
    assert key.position.hand is Hand.LEFT
    assert key.position.finger is Finger.PINKY
    assert key.position.row is Row.TOP
    assert key.position.column == 1


def test_mapper_is_case_insensitive():
    mapper = LayoutKeyMapper(
        make_layout()
    )

    upper = mapper.key("A")
    lower = mapper.key("a")

    assert upper == lower


def test_mapper_maps_extra_index_column():
    mapper = LayoutKeyMapper(
        make_layout()
    )

    key_y = mapper.key("Y")
    key_z = mapper.key("Z")

    assert key_y.position.hand is Hand.LEFT
    assert key_y.position.finger is Finger.INDEX
    assert key_y.position.column == 2

    assert key_z.position.hand is Hand.RIGHT
    assert key_z.position.finger is Finger.INDEX
    assert key_z.position.column == 2


def test_mapper_returns_all_26_keys():
    mapper = LayoutKeyMapper(
        make_layout()
    )

    keys = mapper.keys()

    assert len(keys) == 26
    assert {key.id for key in keys} == set(
        string.ascii_uppercase
    )


def test_mapper_preserves_layout_layer():
    mapper = LayoutKeyMapper(
        make_layout(layer="L1")
    )

    key = mapper.key("A")

    assert key.position.layer is Layer.L1


def test_mapper_rejects_unknown_layer():
    layout = make_layout(
        layer="INVALID"
    )

    with pytest.raises(
        ValueError,
        match="Unknown layout layer",
    ):
        LayoutKeyMapper(layout)


def test_mapper_unknown_letter():
    mapper = LayoutKeyMapper(
        make_layout()
    )

    with pytest.raises(
        KeyError,
        match="Unknown letter",
    ):
        mapper.key("@")


def test_key_returns_cached_logical_key():
    layout = make_layout()
    mapper = LayoutKeyMapper(
        layout
    )

    first = mapper.key("A")
    second = mapper.key("A")

    assert first is second


def test_key_cache_uses_normalized_letter():
    layout = make_layout()
    mapper = LayoutKeyMapper(
        layout
    )

    upper = mapper.key("A")
    lower = mapper.key("a")

    assert upper is lower