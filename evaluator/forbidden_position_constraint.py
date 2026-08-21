# evaluator/forbidden_position_constraint.py

from __future__ import annotations

from models.constraint_evaluation import ConstraintEvaluation
from models.constraint_violation import ConstraintViolation
from models.layout import Layout


class ForbiddenPositionConstraint:
    """
    Reject letters assigned to forbidden logical positions.

    Forbidden positions are supplied from outside so that the
    constraint itself does not contain keyboard-specific policy.
    """

    def __init__(
        self,
        forbidden_positions: frozenset[str],
    ) -> None:
        self._forbidden_positions = forbidden_positions

    @property
    def forbidden_positions(self) -> frozenset[str]:
        return self._forbidden_positions

    def evaluate(
        self,
        layout: Layout,
    ) -> ConstraintEvaluation:
        """
        Evaluate a layout against the forbidden-position set.
        """

        violations: list[ConstraintViolation] = []

        for letter, position in layout.items():
            if position not in self._forbidden_positions:
                continue

            violations.append(
                ConstraintViolation(
                    constraint="forbidden_position",
                    message=(
                        f"{letter} is assigned to forbidden "
                        f"position {position}."
                    ),
                    letter=letter,
                    position=position,
                )
            )

        return ConstraintEvaluation(
            violations=tuple(violations)
        )