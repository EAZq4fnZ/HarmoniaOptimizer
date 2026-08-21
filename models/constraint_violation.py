# models/constraint_violation.py

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ConstraintViolation:
    """
    Represents one hard-constraint violation.

    A hard constraint is a rule that a layout must satisfy.
    Unlike a soft cost, a violation makes the layout invalid.
    """

    constraint: str
    message: str
    letter: str | None = None
    position: str | None = None

    def __post_init__(self) -> None:
        if not self.constraint.strip():
            raise ValueError(
                "constraint must not be empty"
            )

        if not self.message.strip():
            raise ValueError(
                "message must not be empty"
            )