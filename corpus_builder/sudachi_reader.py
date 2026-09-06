from __future__ import annotations

import unicodedata
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

    def is_oov(
        self,
    ) -> bool:
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



SMALL_HIRAGANA = frozenset(
    "ぁぃぅぇぉ"
    "ゃゅょ"
    "ゎ"
)

SMALL_KATAKANA = frozenset(
    "ァィゥェォ"
    "ャュョ"
    "ヮ"
)

SUPPORTED_JAPANESE_AUXILIARY_CHARACTERS = (
    SMALL_HIRAGANA
    | SMALL_KATAKANA
    | frozenset(
        {
            "っ",
            "ッ",
            "ー",
        }
    )
)

SPECIAL_HIRAGANA = frozenset(
    {
        "っ",
        "ゔ",
        "ゝ",
        "ゞ",
        "゛",
        "゜",
    }
)


def is_plain_hiragana(
    text: str,
) -> bool:
    return bool(text) and all(
        (
            "\u3040" <= char <= "\u309f"
            and char not in SMALL_HIRAGANA
            and char not in SPECIAL_HIRAGANA
        )
        for char in text
    )


def hiragana_to_katakana(
    text: str,
) -> str:
    return "".join(
        chr(
            ord(char) + 0x60
        )
        for char in text
    )



def is_punctuation_or_symbol_text(
    text: str,
) -> bool:
    return bool(text) and all(
        unicodedata.category(
            char
        )[0]
        in {"P", "S"}
        for char in text
    )


def select_sudachi_corpus_part(
    morpheme: SudachiMorpheme,
) -> str | None:
    surface = morpheme.surface()

    if not isinstance(
        surface,
        str,
    ):
        raise TypeError(
            "Sudachi surface must be a string"
        )

    part_of_speech = morpheme.part_of_speech()

    if not surface:
        if part_of_speech[0] == "補助記号":
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

            return reading

        raise ValueError(
            "Sudachi surface must not be empty"
        )

    if surface.isspace():
        return None

    if part_of_speech[0] == "補助記号":
        if all(
            char
            in SUPPORTED_JAPANESE_AUXILIARY_CHARACTERS
            for char in surface
        ):
            return surface

        if is_punctuation_or_symbol_text(
            surface
        ):
            return surface

        return None

    if surface.isascii():
        return surface

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

    if (
        morpheme.is_oov()
        and reading == surface
        and is_plain_hiragana(
            surface
        )
    ):
        return hiragana_to_katakana(
            surface
        )

    return reading


def extract_sudachi_corpus_parts(
    morphemes: Iterable[SudachiMorpheme],
) -> Iterable[str]:
    for morpheme in morphemes:
        part = select_sudachi_corpus_part(
            morpheme
        )

        if part is not None:
            yield part


SUDACHI_TEXT_MAX_BYTES = 48_000


def split_text_by_utf8_bytes(
    text: str,
    *,
    max_bytes: int = SUDACHI_TEXT_MAX_BYTES,
) -> tuple[str, ...]:
    if max_bytes <= 0:
        raise ValueError(
            "max_bytes must be greater than 0"
        )

    if not text:
        return ()

    if len(
        text.encode("utf-8")
    ) <= max_bytes:
        return (text,)

    chunks: list[str] = []
    start = 0

    while start < len(text):
        low = start + 1
        high = len(text)
        best = start

        while low <= high:
            middle = (
                low + high
            ) // 2

            candidate = text[
                start:middle
            ]

            if len(
                candidate.encode("utf-8")
            ) <= max_bytes:
                best = middle
                low = middle + 1
            else:
                high = middle - 1

        if best == start:
            raise ValueError(
                "Single character exceeds byte limit"
            )

        chunks.append(
            text[start:best]
        )

        start = best

    return tuple(chunks)


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
        for chunk in split_text_by_utf8_bytes(
            text
        ):
            yield from extract_sudachi_corpus_parts(
                tokenizer.tokenize(chunk)
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
