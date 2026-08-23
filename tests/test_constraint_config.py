# tests/test_constraint_config.py

import pytest

from models.constraint_config import (
    ConstraintConfig,
    ForbiddenPositionConstraintConfig,
    VowelPositionConstraintConfig,
)


def make_config() -> ConstraintConfig:
    return ConstraintConfig(
        version="1.0",
        vowel_position=VowelPositionConstraintConfig(
            enabled=True,
            allowed_positions=frozenset({
                "L-M-H-2",
                "L-I-H-3",
            }),
        ),
        forbidden_position=ForbiddenPositionConstraintConfig(
            enabled=True,
            forbidden_positions=frozenset({
                "L-P-T-0",
                "R-P-T-0",
            }),
        ),
    )


def test_constraint_config_attributes():
    config = make_config()

    assert config.version == "1.0"

    assert config.vowel_position.enabled is True

    assert (
        "L-M-H-2"
        in config.vowel_position.allowed_positions
    )

    assert (
        config.forbidden_position.enabled
        is True
    )

    assert (
        "L-P-T-0"
        in config.forbidden_position.forbidden_positions
    )


def test_empty_version_is_rejected():
    with pytest.raises(
        ValueError,
        match="version",
    ):
        ConstraintConfig(
            version="",
            vowel_position=VowelPositionConstraintConfig(
                enabled=False,
                allowed_positions=frozenset(),
            ),
            forbidden_position=ForbiddenPositionConstraintConfig(
                enabled=False,
                forbidden_positions=frozenset(),
            ),
        )


def test_whitespace_version_is_rejected():
    with pytest.raises(
        ValueError,
        match="version",
    ):
        ConstraintConfig(
            version="   ",
            vowel_position=VowelPositionConstraintConfig(
                enabled=False,
                allowed_positions=frozenset(),
            ),
            forbidden_position=ForbiddenPositionConstraintConfig(
                enabled=False,
                forbidden_positions=frozenset(),
            ),
        )


def test_constraint_config_is_immutable():
    config = make_config()

    with pytest.raises(AttributeError):
        config.version = "2.0"