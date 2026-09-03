from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Protocol


class SudachiMorpheme(Protocol):
    def surface(
        self,
    ) -> str:
        ...

    def reading_form(
        self,
    ) -> str:
        ...

    def part_of_speech(
        self,
    ) -> tuple[str, ...]:
        ...


def extract_sudachi_readings(
    morphemes: Iterable[SudachiMorpheme],
) -> Iterable[str]:
    for morpheme in morphemes:
        reading = morpheme.reading_form()

        if not isinstance(
            reading,
            str,
        ):
            raise TypeError(
                "Sudachi reading must be a string"
            )

        if not reading:
            raise ValueError(
                "Sudachi reading must not be empty"
            )

        yield reading



def extract_sudachi_corpus_parts(
    morphemes: Iterable[SudachiMorpheme],
) -> Iterable[str]:
    for morpheme in morphemes:
        surface = morpheme.surface()

        if not isinstance(
            surface,
            str,
        ):
            raise TypeError(
                "Sudachi surface must be a string"
            )

        if not surface:
            raise ValueError(
                "Sudachi surface must not be empty"
            )

        if surface.isspace():
            continue

        part_of_speech = morpheme.part_of_speech()

        if part_of_speech[0] == "補助記号":
            yield surface
            continue

        if surface.isascii():
            yield surface
            continue

        reading = morpheme.reading_form()

        if not isinstance(
            reading,
            str,
        ):
            raise TypeError(
                "Sudachi reading must be a string"
            )

        if not reading:
            raise ValueError(
                "Sudachi reading must not be empty"
            )

        yield reading


class SudachiTokenizer(Protocol):
    def tokenize(
        self,
        text: str,
    ) -> Iterable[SudachiMorpheme]:
        ...


def make_sudachi_tokenizer(
    tokenizer: SudachiTokenizer,
) -> Callable[[str], Iterable[str]]:
    def read(
        text: str,
    ) -> Iterable[str]:
        return extract_sudachi_corpus_parts(
            tokenizer.tokenize(text)
        )

    return read



def make_default_sudachi_tokenizer() -> Callable[[str], Iterable[str]]:
    from sudachipy import Dictionary, SplitMode

    tokenizer = Dictionary(
        dict="core"
    ).create(
        mode=SplitMode.C
    )

    return make_sudachi_tokenizer(
        tokenizer
    )
