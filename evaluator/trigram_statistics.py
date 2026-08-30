from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field


@dataclass(slots=True)
class TrigramStatistics:
    """
    Accumulate raw and weighted trigram frequencies.

    Trigrams are stored using normalized uppercase character IDs.

    Example:
        "the" -> ("T", "H", "E")

    raw_count records the number of observed occurrences.
    weighted_count records the corpus-weighted occurrence count.
    """

    _raw_counts: dict[tuple[str, str, str], int] = field(
        default_factory=dict
    )
    _weighted_counts: dict[tuple[str, str, str], float] = field(
        default_factory=dict
    )

    def record(
        self,
        first: str,
        second: str,
        third: str,
        weight: float = 1.0,
    ) -> None:
        """
        Record one trigram occurrence.
        """

        if weight < 0.0:
            raise ValueError("weight must be non-negative")

        first_id = self._normalize(first)
        second_id = self._normalize(second)
        third_id = self._normalize(third)

        key = (
            first_id,
            second_id,
            third_id,
        )

        self._raw_counts[key] = (
            self._raw_counts.get(key, 0) + 1
        )

        self._weighted_counts[key] = (
            self._weighted_counts.get(key, 0.0)
            + weight
        )

    def raw_count(
        self,
        first: str,
        second: str,
        third: str,
    ) -> int:
        """
        Return the raw occurrence count for one trigram.
        """

        key = self._normalized_key(
            first,
            second,
            third,
        )

        return self._raw_counts.get(key, 0)

    def weighted_count(
        self,
        first: str,
        second: str,
        third: str,
    ) -> float:
        """
        Return the weighted occurrence count for one trigram.
        """

        key = self._normalized_key(
            first,
            second,
            third,
        )

        return self._weighted_counts.get(key, 0.0)

    @property
    def total_raw_count(self) -> int:
        """
        Return the total number of recorded trigram occurrences.
        """

        return sum(self._raw_counts.values())

    @property
    def total_weighted_count(self) -> float:
        """
        Return the total weighted trigram occurrence count.
        """

        return sum(self._weighted_counts.values())

    def evaluation_records(
        self,
    ) -> Iterator[
        tuple[str, str, str, int, float]
    ]:
        """
        Yield deterministic records for evaluation.

        Each record contains:

            first
            second
            third
            raw_count
            weighted_count
        """

        for key in sorted(self._raw_counts):
            first, second, third = key

            yield (
                first,
                second,
                third,
                self._raw_counts[key],
                self._weighted_counts.get(key, 0.0),
            )

    def __len__(self) -> int:
        """
        Return the number of unique trigrams.
        """

        return len(self._raw_counts)

    @staticmethod
    def _normalize(
        character: str,
    ) -> str:
        if len(character) != 1:
            raise ValueError(
                "trigram characters must contain exactly one character"
            )

        return character.upper()

    @classmethod
    def _normalized_key(
        cls,
        first: str,
        second: str,
        third: str,
    ) -> tuple[str, str, str]:
        return (
            cls._normalize(first),
            cls._normalize(second),
            cls._normalize(third),
        )
