# models/constraint_config.py

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class VowelPositionConstraintConfig:
    enabled: bool
    allowed_positions: frozenset[str]


@dataclass(frozen=True, slots=True)
class ForbiddenPositionConstraintConfig:
    enabled: bool
    forbidden_positions: frozenset[str]


@dataclass(frozen=True, slots=True)
class VowelHandDistributionConstraintConfig:
    enabled: bool = False
    min_left_vowels: int = 0
    max_left_vowels: int = 5

    def __post_init__(self) -> None:
        if self.min_left_vowels < 0:
            raise ValueError(
                "min_left_vowels must be greater than "
                "or equal to 0"
            )

        if self.max_left_vowels > 5:
            raise ValueError(
                "max_left_vowels must not exceed 5"
            )

        if self.min_left_vowels > self.max_left_vowels:
            raise ValueError(
                "min_left_vowels must not exceed "
                "max_left_vowels"
            )


@dataclass(frozen=True, slots=True)
class ConstraintConfig:
    version: str
    vowel_position: VowelPositionConstraintConfig
    forbidden_position: ForbiddenPositionConstraintConfig
    vowel_hand_distribution: (
        VowelHandDistributionConstraintConfig
    ) = field(
        default_factory=(
            VowelHandDistributionConstraintConfig
        )
    )

    def __post_init__(self) -> None:
        if not self.version.strip():
            raise ValueError(
                "version must not be empty"
            )