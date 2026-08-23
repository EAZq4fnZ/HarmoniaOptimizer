# models/constraint_config.py

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VowelPositionConstraintConfig:
    enabled: bool
    allowed_positions: frozenset[str]


@dataclass(frozen=True, slots=True)
class ForbiddenPositionConstraintConfig:
    enabled: bool
    forbidden_positions: frozenset[str]


@dataclass(frozen=True, slots=True)
class ConstraintConfig:
    version: str
    vowel_position: VowelPositionConstraintConfig
    forbidden_position: ForbiddenPositionConstraintConfig

    def __post_init__(self) -> None:
        if not self.version.strip():
            raise ValueError(
                "version must not be empty"
            )