# tests/test_constraint_factory.py

from evaluator.constraint_factory import ConstraintFactory
from evaluator.constraint_set import ConstraintSet
from evaluator.forbidden_position_constraint import (
    ForbiddenPositionConstraint,
)
from evaluator.vowel_hand_distribution_constraint import (
    VowelHandDistributionConstraint,
)
from evaluator.vowel_position_constraint import (
    VowelPositionConstraint,
)
from models.constraint_config import (
    ConstraintConfig,
    ForbiddenPositionConstraintConfig,
    VowelHandDistributionConstraintConfig,
    VowelPositionConstraintConfig,
)


def make_config(
    *,
    vowel_enabled: bool = True,
    forbidden_enabled: bool = True,
) -> ConstraintConfig:
    return ConstraintConfig(
        version="1.0",
        vowel_position=VowelPositionConstraintConfig(
            enabled=vowel_enabled,
            allowed_positions=frozenset({
                "L-I-T-3",
                "L-M-H-2",
                "R-I-T-3",
                "R-M-H-2",
                "R-R-H-1",
            }),
        ),
        forbidden_position=(
            ForbiddenPositionConstraintConfig(
                enabled=forbidden_enabled,
                forbidden_positions=frozenset({
                    "L-P-T-0",
                    "R-P-T-0",
                }),
            )
        ),
    )


def test_create_returns_constraint_set():
    result = ConstraintFactory.create(
        make_config()
    )

    assert isinstance(
        result,
        ConstraintSet,
    )


def test_create_with_both_enabled():
    result = ConstraintFactory.create(
        make_config()
    )

    assert len(result.constraints) == 2

    assert isinstance(
        result.constraints[0],
        VowelPositionConstraint,
    )

    assert isinstance(
        result.constraints[1],
        ForbiddenPositionConstraint,
    )


def test_create_preserves_vowel_positions():
    config = make_config()

    result = ConstraintFactory.create(
        config
    )

    vowel_constraint = result.constraints[0]

    assert isinstance(
        vowel_constraint,
        VowelPositionConstraint,
    )

    assert (
        vowel_constraint.allowed_positions
        == config.vowel_position.allowed_positions
    )


def test_create_preserves_forbidden_positions():
    config = make_config()

    result = ConstraintFactory.create(
        config
    )

    forbidden_constraint = result.constraints[1]

    assert isinstance(
        forbidden_constraint,
        ForbiddenPositionConstraint,
    )

    assert (
        forbidden_constraint.forbidden_positions
        == config
        .forbidden_position
        .forbidden_positions
    )


def test_create_with_vowel_disabled():
    result = ConstraintFactory.create(
        make_config(
            vowel_enabled=False,
        )
    )

    assert len(result.constraints) == 1

    assert isinstance(
        result.constraints[0],
        ForbiddenPositionConstraint,
    )


def test_create_with_forbidden_disabled():
    result = ConstraintFactory.create(
        make_config(
            forbidden_enabled=False,
        )
    )

    assert len(result.constraints) == 1

    assert isinstance(
        result.constraints[0],
        VowelPositionConstraint,
    )


def test_create_with_all_disabled():
    result = ConstraintFactory.create(
        make_config(
            vowel_enabled=False,
            forbidden_enabled=False,
        )
    )

    assert result.constraints == ()


def test_create_returns_new_constraint_set():
    config = make_config()

    first = ConstraintFactory.create(
        config
    )

    second = ConstraintFactory.create(
        config
    )

    assert first is not second


def test_create_returns_new_constraints():
    config = make_config()

    first = ConstraintFactory.create(
        config
    )

    second = ConstraintFactory.create(
        config
    )

    assert (
        first.constraints[0]
        is not second.constraints[0]
    )

    assert (
        first.constraints[1]
        is not second.constraints[1]
    )


def test_create_with_vowel_hand_distribution_enabled():
    config = ConstraintConfig(
        version="1.0",
        vowel_position=VowelPositionConstraintConfig(
            enabled=False,
            allowed_positions=frozenset(),
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

    result = ConstraintFactory.create(
        config
    )

    assert len(result.constraints) == 1

    assert isinstance(
        result.constraints[0],
        VowelHandDistributionConstraint,
    )


def test_create_preserves_vowel_hand_distribution_limits():
    config = ConstraintConfig(
        version="1.0",
        vowel_position=VowelPositionConstraintConfig(
            enabled=False,
            allowed_positions=frozenset(),
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

    result = ConstraintFactory.create(
        config
    )

    constraint = result.constraints[0]

    assert isinstance(
        constraint,
        VowelHandDistributionConstraint,
    )

    assert constraint.min_left_vowels == 2
    assert constraint.max_left_vowels == 3