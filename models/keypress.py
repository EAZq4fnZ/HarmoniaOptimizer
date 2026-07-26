"""
keypress.py

Harmonia Optimizer

Represents a single logical key press produced from the corpus.

Responsibilities
----------------
- Store the original character.
- Store the assigned logical position.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KeyPress:
    """
    Represents one logical key press.

    Example
    -------
    Letter:
        A

    Logical position:
        L-M-M
    """

    letter: str
    position: str

    def __repr__(self) -> str:
        return (
            f"KeyPress("
            f"letter='{self.letter}', "
            f"position='{self.position}')"
        )