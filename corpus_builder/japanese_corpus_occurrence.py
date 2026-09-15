from __future__ import annotations

from dataclasses import dataclass

from corpus_builder.japanese_corpus_part import (
    JapaneseCorpusPart,
)


@dataclass(frozen=True, slots=True)
class JapaneseCorpusOccurrence:
    """A Japanese corpus part located in its source document."""

    part: JapaneseCorpusPart
    source_start: int
    source_end: int

    def __post_init__(
        self,
    ) -> None:
        if self.source_start < 0:
            raise ValueError(
                "source_start must not be negative"
            )

        if self.source_end < self.source_start:
            raise ValueError(
                "source_end must not be less than source_start"
            )

    def validate_source(
        self,
        source_text: str,
    ) -> None:
        """Verify that this occurrence points at its source span."""
        if self.source_end > len(source_text):
            raise ValueError(
                "source_end exceeds source text length"
            )

        actual = source_text[
            self.source_start:self.source_end
        ]

        if actual != self.part.source_text:
            raise ValueError(
                "source span does not match part source_text"
            )
