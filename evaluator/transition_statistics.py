# transition_statistics.py
from collections import Counter


class TransitionStatistics:
    """Store raw and weighted transition statistics."""

    def __init__(self) -> None:
        self._raw: Counter[tuple[str, str]] = Counter()
        self._weighted: Counter[tuple[str, str]] = Counter()

    def add(
        self,
        transitions: dict[tuple[str, str], int],
        weight: float = 1.0,
    ) -> None:
        """Add transition counts with a weight."""
        for transition, count in transitions.items():
            self._raw[transition] += count
            self._weighted[transition] += count * weight

    def raw_count(self, first: str, second: str) -> int:
        """Return the raw transition count."""
        return self._raw[(first, second)]

    def weighted_count(self, first: str, second: str) -> float:
        """Return the weighted transition count."""
        return self._weighted[(first, second)]

    def raw(self) -> dict[tuple[str, str], int]:
        """Return raw transition counts."""
        return dict(self._raw)

    def weighted(self) -> dict[tuple[str, str], float]:
        """Return weighted transition counts."""
        return dict(self._weighted)

    def clear(self) -> None:
        """Clear all statistics."""
        self._raw.clear()
        self._weighted.clear()