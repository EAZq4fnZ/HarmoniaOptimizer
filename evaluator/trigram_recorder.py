from __future__ import annotations

from collections.abc import Iterator

from .trigram_statistics import TrigramStatistics


class TrigramRecorder:
    """
    Record overlapping three-character sequences from text.

    Example:
        "THE" produces:

            T H E

        "THERE" produces:

            T H E
            H E R
            E R E

    Only alphabetic A-Z trigrams are currently recorded.
    A non-A-Z character breaks the trigram sequence.
    """

    def record(
        self,
        text: str,
        statistics: TrigramStatistics,
        weight: float = 1.0,
    ) -> None:
        """
        Record all overlapping A-Z trigrams from text.
        """

        if weight < 0.0:
            raise ValueError("weight must be non-negative")

        normalized = text.upper()

        for first, second, third in self._windows(normalized):
            if not (
                self._is_ascii_letter(first)
                and self._is_ascii_letter(second)
                and self._is_ascii_letter(third)
            ):
                continue

            statistics.record(
                first,
                second,
                third,
                weight=weight,
            )

    @staticmethod
    def _windows(
        text: str,
    ) -> Iterator[tuple[str, str, str]]:
        for index in range(len(text) - 2):
            yield (
                text[index],
                text[index + 1],
                text[index + 2],
            )

    @staticmethod
    def _is_ascii_letter(
        character: str,
    ) -> bool:
        return (
            "A" <= character <= "Z"
        )
