# models/constraint_evaluation.py

from __future__ import annotations

from dataclasses import dataclass

from models.constraint_violation import ConstraintViolation


@dataclass(frozen=True, slots=True)
class ConstraintEvaluation:
    """
    Result of evaluating one or more hard constraints.

    A layout is valid when no violations are present.
    """

    violations: tuple[ConstraintViolation, ...] = ()

    @property
    def is_valid(self) -> bool:
        """
        Return True when no hard-constraint violations exist.
        """

        return not self.violations

    @property
    def violation_count(self) -> int:
        """
        Return the number of violations.
        """

        return len(self.violations)