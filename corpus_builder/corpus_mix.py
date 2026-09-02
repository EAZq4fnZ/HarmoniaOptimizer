from __future__ import annotations

import math
from dataclasses import dataclass

from models.corpus import Corpus
from models.corpus_entry import CorpusEntry

from .text_metrics import count_ascii_letters


@dataclass(frozen=True, slots=True)
class CorpusMixSource:
    text: str
    target_ratio: float

    def __post_init__(self) -> None:
        if self.target_ratio <= 0:
            raise ValueError(
                "target_ratio must be greater than 0"
            )


@dataclass(frozen=True, slots=True)
class CorpusMix:
    sources: tuple[CorpusMixSource, ...]

    def __post_init__(self) -> None:
        if not self.sources:
            raise ValueError(
                "Corpus mix must contain at least one source"
            )

        total_ratio = sum(
            source.target_ratio
            for source in self.sources
        )

        if not math.isclose(
            total_ratio,
            1.0,
        ):
            raise ValueError(
                "target ratios must sum to 1.0"
            )

    def build(self) -> Corpus:
        entries: list[CorpusEntry] = []

        for source in self.sources:
            ascii_letter_count = count_ascii_letters(
                source.text
            )

            if ascii_letter_count == 0:
                raise ValueError(
                    "Corpus mix source must contain at least one ASCII letter"
                )

            entries.append(
                CorpusEntry(
                    text=source.text,
                    weight=(
                        source.target_ratio
                        / ascii_letter_count
                    ),
                )
            )

        return Corpus(
            entries=tuple(entries)
        )
