"""
corpus_parser.py

Harmonia Optimizer

Convert corpus text into a sequence of logical key presses.
"""

from __future__ import annotations

from models.keypress import KeyPress
from models.layout import Layout


class CorpusParser:
    """
    Convert text into KeyPress objects.

    Example
    -------
    Input:
        "Hello, World!"

    Output:
        [
            KeyPress("H", "R-Ii-M"),
            KeyPress("E", "R-Ii-U"),
            ...
        ]
    """

    def __init__(self, layout: Layout):
        self.layout = layout

    # --------------------------------------------------------

    def parse(self, text: str) -> list[KeyPress]:
        """
        Parse text into KeyPress sequence.

        Non-alphabetic characters are ignored.
        """

        result: list[KeyPress] = []

        for char in text.upper():

            if char not in self.layout:
                continue

            result.append(
                KeyPress(
                    letter=char,
                    position=self.layout.position(char),
                )
            )

        return result

    # --------------------------------------------------------

    def parse_file(self, path: str) -> list[KeyPress]:
        """
        Parse a UTF-8 text file.
        """

        with open(path, "r", encoding="utf-8") as f:
            return self.parse(f.read())