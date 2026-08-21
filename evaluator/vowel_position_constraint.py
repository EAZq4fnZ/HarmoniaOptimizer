# evaluator/vowel_position_constraint.py

from __future__ import annotations

from models.constraint_evaluation import ConstraintEvaluation
from models.constraint_violation import ConstraintViolation
from models.layout import Layout


class VowelPositionConstraint:
    """
    Restrict vowels to explicitly allowed logical positions.

    The constraint does not decide which positions are desirable.
    That policy is supplied through allowed_positions.
    """

    VOWELS = frozenset({"A", "E", "I", "O", "U"})

    def __init__(
        self,
        allowed_positions: frozenset[str],
    ) -> None:
        self._allowed_positions = allowed_positions

    @property
    def allowed_positions(self) -> frozenset[str]:
        return self._allowed_positions

    def evaluate(
        self,
        layout: Layout,
    ) -> ConstraintEvaluation:
        """
        Evaluate vowel positions in the given layout.
        """

        violations: list[ConstraintViolation] = []

        for vowel in self.VOWELS:
            position = layout.position(vowel)

            if position in self._allowed_positions:
                continue

            violations.append(
                ConstraintViolation(
                    constraint="vowel_position",
                    message=(
                        f"{vowel} is assigned to disallowed "
                        f"vowel position {position}."
                    ),
                    letter=vowel,
                    position=position,
                )
            )

        return ConstraintEvaluation(
            violations=tuple(violations)
        )