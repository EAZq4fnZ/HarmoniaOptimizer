# models/corpus.py
from dataclasses import dataclass

from .corpus_entry import CorpusEntry


@dataclass(frozen=True, slots=True)
class Corpus:
    entries: tuple[CorpusEntry, ...]

    def __post_init__(self) -> None:
        if not self.entries:
            raise ValueError("Corpus must contain at least one entry.")

    @property
    def total_weight(self) -> float:
        return sum(entry.weight for entry in self.entries)

    @property
    def total_characters(self) -> int:
        return sum(len(entry.text) for entry in self.entries)