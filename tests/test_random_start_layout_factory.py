from __future__ import annotations

import string

import pytest

from models.layout import Layout
from optimizer.random_start_layout_factory import (
    RandomStartLayoutFactory,
)


def make_base_layout() -> Layout:
    positions = [
        f"P-{index:02d}"
        for index in range(26)
    ]

    return Layout(
        name="base",
        version="1.0",
        layer="L0",
        description="Base description",
        mapping=dict(
            zip(
                string.ascii_uppercase,
                positions,
                strict=True,
            )
        ),
    )


def test_rejects_negative_run_index() -> None:
    factory = RandomStartLayoutFactory(
        seed=12345
    )

    with pytest.raises(
        ValueError,
        match=(
            "run_index must be greater "
            "than or equal to 0"
        ),
    ):
        factory.create(
            base_layout=make_base_layout(),
            run_index=-1,
        )


def test_same_seed_and_run_index_are_reproducible() -> None:
    base = make_base_layout()

    first_factory = (
        RandomStartLayoutFactory(
            seed=12345
        )
    )

    second_factory = (
        RandomStartLayoutFactory(
            seed=12345
        )
    )

    first = first_factory.create(
        base_layout=base,
        run_index=7,
    )

    second = second_factory.create(
        base_layout=base,
        run_index=7,
    )

    assert first.mapping == second.mapping


def test_result_does_not_depend_on_call_order() -> None:
    base = make_base_layout()

    sequential_factory = (
        RandomStartLayoutFactory(
            seed=12345
        )
    )

    for run_index in range(7):
        sequential_factory.create(
            base_layout=base,
            run_index=run_index,
        )

    sequential = (
        sequential_factory.create(
            base_layout=base,
            run_index=7,
        )
    )

    direct_factory = (
        RandomStartLayoutFactory(
            seed=12345
        )
    )

    direct = direct_factory.create(
        base_layout=base,
        run_index=7,
    )

    assert (
        sequential.mapping
        == direct.mapping
    )


def test_different_run_indices_produce_different_layouts() -> None:
    base = make_base_layout()

    factory = RandomStartLayoutFactory(
        seed=12345
    )

    first = factory.create(
        base_layout=base,
        run_index=0,
    )

    second = factory.create(
        base_layout=base,
        run_index=1,
    )

    assert first.mapping != second.mapping


def test_preserves_letters_and_positions() -> None:
    base = make_base_layout()

    factory = RandomStartLayoutFactory(
        seed=12345
    )

    result = factory.create(
        base_layout=base,
        run_index=3,
    )

    assert (
        set(result.mapping)
        == set(base.mapping)
    )

    assert (
        set(result.mapping.values())
        == set(base.mapping.values())
    )


def test_preserves_layout_metadata() -> None:
    base = make_base_layout()

    factory = RandomStartLayoutFactory(
        seed=12345
    )

    result = factory.create(
        base_layout=base,
        run_index=3,
    )

    assert result.version == base.version
    assert result.layer == base.layer
    assert (
        result.description
        == base.description
    )

    assert (
        result.name
        == "base_random_0003"
    )


def test_does_not_modify_base_layout() -> None:
    base = make_base_layout()
    original_mapping = dict(
        base.mapping
    )

    factory = RandomStartLayoutFactory(
        seed=12345
    )

    factory.create(
        base_layout=base,
        run_index=5,
    )

    assert base.mapping == original_mapping
