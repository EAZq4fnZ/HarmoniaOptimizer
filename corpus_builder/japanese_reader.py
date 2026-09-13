from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from .japanese_corpus_part import JapaneseCorpusPart
from .sudachi_reader import (
    make_default_sudachi_corpus_part_tokenizer,
    make_default_sudachi_tokenizer,
)


@dataclass(frozen=True, slots=True)
class JapaneseReader:
    tokenizer: Callable[[str], Iterable[str]]
    part_tokenizer: (
        Callable[
            [str],
            Iterable[JapaneseCorpusPart],
        ]
        | None
    ) = None

    def __call__(
        self,
        text: str,
    ) -> str:
        return "".join(
            self.tokenizer(text)
        )

    def read_parts(
        self,
        text: str,
    ) -> tuple[JapaneseCorpusPart, ...]:
        if self.part_tokenizer is None:
            raise RuntimeError(
                "JapaneseReader does not have "
                "a structured tokenizer"
            )

        return tuple(
            self.part_tokenizer(text)
        )


def make_default_japanese_reader() -> JapaneseReader:
    return JapaneseReader(
        tokenizer=make_default_sudachi_tokenizer(),
        part_tokenizer=(
            make_default_sudachi_corpus_part_tokenizer()
        ),
    )
