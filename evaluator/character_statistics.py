# evaluator/character_statistics.py

from collections import Counter


class CharacterStatistics:
    """
    Store raw and weighted character frequencies.

    Raw count:
        Actual number of occurrences.

    Weighted count:
        Occurrences multiplied by corpus entry weight.
    """

    def __init__(self) -> None:
        self._raw: Counter[str] = Counter()
        self._weighted: Counter[str] = Counter()

    def add(
        self,
        counts: dict[str, int],
        *,
        weight: float = 1.0,
    ) -> None:
        """
        Add character counts.
        """

        for character, count in counts.items():
            self._raw[character] += count
            self._weighted[character] += count * weight

    def raw_count(
        self,
        character: str,
    ) -> int:
        """
        Return raw frequency of a character.
        """

        return self._raw[character]

    def weighted_count(
        self,
        character: str,
    ) -> float:
        """
        Return weighted frequency of a character.
        """

        return self._weighted[character]

    def raw(self) -> dict[str, int]:
        """
        Return all raw character frequencies.
        """

        return dict(self._raw)

    def weighted(self) -> dict[str, float]:
        """
        Return all weighted character frequencies.
        """

        return dict(self._weighted)

    def total_raw(self) -> int:
        """
        Return total raw character count.
        """

        return sum(self._raw.values())

    def total_weighted(self) -> float:
        """
        Return total weighted character count.
        """

        return sum(self._weighted.values())

    def clear(self) -> None:
        """
        Remove all recorded statistics.
        """

        self._raw.clear()
        self._weighted.clear()