# evaluator/vowel_hand_distribution_constraint.py

from __future__ import annotations

from models.constraint_evaluation import ConstraintEvaluation
from models.constraint_violation import ConstraintViolation
from models.layout import Layout


class VowelHandDistributionConstraint:
    """
    Restrict how many vowels may be assigned to the left hand.

    With five vowels, for example:

        min_left_vowels = 2
        max_left_vowels = 3

    allows only:

        left 2 / right 3
        left 3 / right 2
    """

    VOWELS = frozenset({
        "A",
        "E",
        "I",
        "O",
        "U",
    })

    def __init__(
        self,
        min_left_vowels: int,
        max_left_vowels: int,
    ) -> None:
        if min_left_vowels < 0:
            raise ValueError(
                "min_left_vowels must be greater than "
                "or equal to 0"
            )

        if max_left_vowels > len(self.VOWELS):
            raise ValueError(
                "max_left_vowels must not exceed "
                "the number of vowels"
            )

        if min_left_vowels > max_left_vowels:
            raise ValueError(
                "min_left_vowels must not exceed "
                "max_left_vowels"
            )

        self._min_left_vowels = min_left_vowels
        self._max_left_vowels = max_left_vowels

    @property
    def min_left_vowels(self) -> int:
        return self._min_left_vowels

    @property
    def max_left_vowels(self) -> int:
        return self._max_left_vowels

    def evaluate(
        self,
        layout: Layout,
    ) -> ConstraintEvaluation:
        left_vowels = tuple(
            vowel
            for vowel in self.VOWELS
            if layout.position(vowel).startswith("L-")
        )

        left_count = len(left_vowels)

        if (
            self._min_left_vowels
            <= left_count
            <= self._max_left_vowels
        ):
            return ConstraintEvaluation(
                violations=()
            )

        right_count = (
            len(self.VOWELS)
            - left_count
        )

        violation = ConstraintViolation(
            constraint="vowel_hand_distribution",
            message=(
                "Vowel hand distribution is outside "
                "the allowed range: "
                f"left={left_count}, "
                f"right={right_count}, "
                f"allowed left="
                f"{self._min_left_vowels}"
                f"..{self._max_left_vowels}."
            ),
        )

        return ConstraintEvaluation(
            violations=(
                violation,
            )
        )