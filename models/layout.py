"""
layout.py

Harmonia Optimizer

Logical keyboard layout loader.

Responsibilities
----------------
- Load layout JSON
- Validate layout integrity
- Convert letter -> logical position
- Convert logical position -> letter
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
import string


# ------------------------------------------------------------
# Data class
# ------------------------------------------------------------

@dataclass(frozen=True)
class Layout:
    """
    Logical keyboard layout.

    Example
    -------
    A -> L-M-M
    B -> R-R-U
    """

    name: str
    version: str
    layer: str
    description: str

    mapping: dict[str, str]

    # Automatically generated reverse lookup.
    reverse_mapping: dict[str, str] = field(init=False)

    # --------------------------------------------------------

    def __post_init__(self) -> None:
        """
        Build reverse lookup table.

        Example
        -------
        L-M-M -> A
        """

        reverse = {
            position: letter
            for letter, position in self.mapping.items()
        }

        object.__setattr__(self, "reverse_mapping", reverse)

        # Always validate after construction.
        self.validate()

    # --------------------------------------------------------

    @classmethod
    def load(cls, path: str | Path) -> "Layout":
        """
        Load layout from JSON.
        """

        path = Path(path)

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        return cls(
            name=data["name"],
            version=data["version"],
            layer=data["layer"],
            description=data.get("description", ""),
            mapping=data["layout"],
        )

    # --------------------------------------------------------

    def validate(self) -> None:
        """
        Validate layout integrity.
        """

        if len(self.mapping) != 26:
            raise ValueError(
                f"Layout must contain exactly 26 letters "
                f"(found {len(self.mapping)})"
            )

        expected = set(string.ascii_uppercase)
        letters = set(self.mapping.keys())

        if letters != expected:

            missing = expected - letters
            extra = letters - expected

            raise ValueError(
                "Invalid alphabet.\n"
                f"Missing: {sorted(missing)}\n"
                f"Extra: {sorted(extra)}"
            )

        positions = list(self.mapping.values())

        if len(positions) != len(set(positions)):
            raise ValueError(
                "Duplicate logical positions detected."
            )

    # --------------------------------------------------------

    def position(self, letter: str) -> str:
        """
        Return logical position assigned to a letter.

        Example
        -------
        layout.position("A")
        -> L-M-M
        """

        letter = letter.upper()

        try:
            return self.mapping[letter]

        except KeyError:
            raise KeyError(
                f"Unknown letter: {letter}"
            ) from None

    # --------------------------------------------------------

    def letter(self, position: str) -> str:
        """
        Return letter assigned to a logical position.

        Example
        -------
        layout.letter("L-M-M")
        -> A
        """

        try:
            return self.reverse_mapping[position]

        except KeyError:
            raise KeyError(
                f"Unknown logical position: {position}"
            ) from None

    # --------------------------------------------------------

    def letters(self):
        """
        Return all letters.
        """

        return self.mapping.keys()

    # --------------------------------------------------------

    def positions(self):
        """
        Return all logical positions.
        """

        return self.reverse_mapping.keys()

    # --------------------------------------------------------

    def items(self):
        """
        Iterate over (letter, position).
        """

        return self.mapping.items()

    # --------------------------------------------------------

    def __contains__(self, letter: str) -> bool:
        return letter.upper() in self.mapping

    # --------------------------------------------------------

    def __getitem__(self, letter: str) -> str:
        return self.position(letter)

    # --------------------------------------------------------

    def __len__(self) -> int:
        return len(self.mapping)

    # --------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"Layout("
            f"name='{self.name}', "
            f"version='{self.version}', "
            f"layer='{self.layer}', "
            f"letters={len(self.mapping)})"
        )

    """ 
        def swap(self, letter1: str, letter2: str) -> "Layout":
            position1 = self.position(letter1)
            position2 = self.position(letter2)
            mapping = {letter: position for letter, position in self.mapping.items()}
            mapping[letter1] = position2
            mapping[letter2] = position1
            return Layout(
                name=self.name,
                version=self.version,
                layer=self.layer,
                description=self.description,
                mapping=mapping,
            )
    """