# transition_recorder.py
from collections import Counter
from itertools import pairwise

from models.corpus_entry import CorpusEntry


class TransitionRecorder:
    """Record adjacent character transitions from text."""

    def __init__(self) -> None:
        self._transitions: Counter[tuple[str, str]] = Counter()

    def record(self, text: str) -> None:
        """Record adjacent character transitions from text."""
        for first, second in pairwise(text):
            self._transitions[(first, second)] += 1

    def record_entry(self, entry: CorpusEntry) -> None:
        """Record transitions from a corpus entry."""
        self.record(entry.text)

    def transitions(self) -> dict[tuple[str, str], int]:
        """Return recorded transition counts."""
        return dict(self._transitions)

    def count(self, first: str, second: str) -> int:
        """Return the count for a specific transition."""
        return self._transitions[(first, second)]

    def total(self) -> int:
        """Return the total number of recorded transitions."""
        return sum(self._transitions.values())

    def clear(self) -> None:
        """Clear all recorded transitions."""
        self._transitions.clear()
