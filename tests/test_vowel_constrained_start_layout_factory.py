from __future__ import annotations

import string

import pytest

from evaluator.constraint_factory import ConstraintFactory
from models.constraint_config import (
    ConstraintConfig,
    ForbiddenPositionConstraintConfig,
    VowelHandDistributionConstraintConfig,
    VowelPositionConstraintConfig,
)
from models.layout import Layout
from optimizer.vowel_constrained_start_layout_factory import (
    VowelConstrainedStartLayoutFactory,
)

VOWELS = frozenset("AEIOU")


def make_base_layout() -> Layout:
    positions = [
        "L-I-T-3",
        "L-I-H-3",
        "L-M-T-2",
        "L-M-H-2",
        "L-R-T-1",
        "L-R-H-1",
        "L-I-B-3",
        "L-M-B-2",
        "L-P-H-0",
        "L-I-T-4",
        "L-I-H-4",
        "L-I-B-4",
        "L-R-B-1",
        "R-I-T-3",
        "R-I-H-3",
        "R-M-T-2",
        "R-M-H-2",
        "R-R-T-1",
        "R-R-H-1",
        "R-I-B-3",
        "R-M-B-2",
        "R-P-H-0",
        "R-I-T-4",
        "R-I-H-4",
        "R-I-B-4",
        "R-R-B-1",
    ]

    return Layout(
        name="base",
        version="1.0",
        layer="L0",
        description="Base layout",
        mapping=dict(
            zip(
                string.ascii_uppercase,
                positions,
                strict=True,
            )
        ),
    )


def make_config() -> ConstraintConfig:
    return ConstraintConfig(
        version="1.0",
        vowel_position=(
            VowelPositionConstraintConfig(
                enabled=True,
                allowed_positions=frozenset({
                    "L-I-T-3",
                    "L-I-H-3",
                    "L-M-H-2",
                    "R-I-T-3",
                    "R-I-H-3",
                    "R-M-H-2",
                }),
            )
        ),
        forbidden_position=(
            ForbiddenPositionConstraintConfig(
                enabled=False,
                forbidden_positions=frozenset(),
            )
        ),
        vowel_hand_distribution=(
            VowelHandDistributionConstraintConfig(
                enabled=True,
                min_left_vowels=2,
                max_left_vowels=3,
            )
        ),
    )


def test_rejects_negative_run_index() -> None:
    factory = VowelConstrainedStartLayoutFactory(
        config=make_config(),
        seed=12345,
    )

    with pytest.raises(
        ValueError,
        match="run_index",
    ):
        factory.create(
            base_layout=make_base_layout(),
            run_index=-1,
        )


def test_generated_layout_satisfies_constraints() -> None:
    config = make_config()

    factory = VowelConstrainedStartLayoutFactory(
        config=config,
        seed=12345,
    )

    constraint_set = ConstraintFactory.create(
        config
    )

    for run_index in range(20):
        layout = factory.create(
            base_layout=make_base_layout(),
            run_index=run_index,
        )

        evaluation = constraint_set.evaluate(
            layout
        )

        assert evaluation.is_valid is True


def test_preserves_letters_and_positions() -> None:
    base = make_base_layout()

    factory = VowelConstrainedStartLayoutFactory(
        config=make_config(),
        seed=12345,
    )

    result = factory.create(
        base_layout=base,
        run_index=3,
    )

    assert set(result.mapping) == set(base.mapping)

    assert (
        set(result.mapping.values())
        == set(base.mapping.values())
    )


def test_is_reproducible_and_order_independent() -> None:
    base = make_base_layout()
    config = make_config()

    sequential_factory = (
        VowelConstrainedStartLayoutFactory(
            config=config,
            seed=12345,
        )
    )

    for run_index in range(7):
        sequential_factory.create(
            base_layout=base,
            run_index=run_index,
        )

    sequential = sequential_factory.create(
        base_layout=base,
        run_index=7,
    )

    direct_factory = (
        VowelConstrainedStartLayoutFactory(
            config=config,
            seed=12345,
        )
    )

    direct = direct_factory.create(
        base_layout=base,
        run_index=7,
    )

    assert sequential.mapping == direct.mapping


def test_rejects_impossible_vowel_distribution() -> None:
    config = ConstraintConfig(
        version="1.0",
        vowel_position=(
            VowelPositionConstraintConfig(
                enabled=True,
                allowed_positions=frozenset({
                    "L-I-H-3",
                    "R-I-H-3",
                    "R-M-H-2",
                    "R-I-T-3",
                    "R-M-T-2",
                }),
            )
        ),
        forbidden_position=(
            ForbiddenPositionConstraintConfig(
                enabled=False,
                forbidden_positions=frozenset(),
            )
        ),
        vowel_hand_distribution=(
            VowelHandDistributionConstraintConfig(
                enabled=True,
                min_left_vowels=2,
                max_left_vowels=3,
            )
        ),
    )

    factory = VowelConstrainedStartLayoutFactory(
        config=config,
        seed=12345,
    )

    with pytest.raises(
        ValueError,
        match="No feasible vowel distribution",
    ):
        factory.create(
            base_layout=make_base_layout(),
            run_index=0,
        )
