# models/corpus_entry.py
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CorpusEntry:
    text: str
    weight: float = 1.0

    def __post_init__(self) -> None:
        if not self.text:
            raise ValueError("Corpus entry text must not be empty.")

        if self.weight <= 0:
            raise ValueError("Corpus entry weight must be greater than 0.")