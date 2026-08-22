# models/swap_move.py

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SwapMove:
    """
    Represents one swap operation between two letters.
    """

    first_letter: str
    second_letter: str

    def __post_init__(self) -> None:
        first = self.first_letter.upper()
        second = self.second_letter.upper()

        if len(first) != 1 or not first.isalpha():
            raise ValueError(
                "first_letter must be a single alphabetic character"
            )

        if len(second) != 1 or not second.isalpha():
            raise ValueError(
                "second_letter must be a single alphabetic character"
            )

        if first == second:
            raise ValueError(
                "swap letters must be different"
            )

        object.__setattr__(
            self,
            "first_letter",
            first,
        )

        object.__setattr__(
            self,
            "second_letter",
            second,
        )

    @property
    def letters(self) -> tuple[str, str]:
        """
        Return the two letters involved in the swap.
        """

        return (
            self.first_letter,
            self.second_letter,
        )