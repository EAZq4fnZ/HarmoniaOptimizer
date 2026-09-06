from __future__ import annotations

from dataclasses import dataclass, field

from .corpus_mix import CorpusMixSource
from .text_metrics import count_ascii_letters


@dataclass(frozen=True, slots=True)
class CorpusBuildResult:
    category: str
    text: str
    source_document_count: int
    ascii_letter_count: int = field(
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.category:
            raise ValueError(
                "category must not be empty"
            )

        if not self.text:
            raise ValueError(
                "text must not be empty"
            )

        if self.source_document_count <= 0:
            raise ValueError(
                "source_document_count must be greater than 0"
            )

        ascii_letter_count = count_ascii_letters(
            self.text
        )

        if ascii_letter_count == 0:
            raise ValueError(
                "text must contain at least one ASCII letter"
            )

        object.__setattr__(
            self,
            "ascii_letter_count",
            ascii_letter_count,
        )

    def to_mix_source(
        self,
        *,
        target_ratio: float,
    ) -> CorpusMixSource:
        return CorpusMixSource(
            text=self.text,
            target_ratio=target_ratio,
        )
