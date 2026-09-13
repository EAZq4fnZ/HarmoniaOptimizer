from __future__ import annotations

from collections.abc import Callable, Iterable

from .japanese_corpus_part import (
    JapaneseCorpusPart,
    JapaneseCorpusPartKind,
)
from .text_normalizer import (
    normalize_fullwidth_ascii,
    normalize_text,
)


def normalize_japanese_source_text(
    text: str,
) -> str:
    return normalize_fullwidth_ascii(
        normalize_text(text)
    )


def preprocess_japanese_corpus_part(
    part: JapaneseCorpusPart,
    *,
    romanizer: Callable[[str], str],
    canonicalizer: Callable[[str], str],
) -> str:
    if (
        part.kind
        is JapaneseCorpusPartKind.JAPANESE_LEXICAL
    ):
        result = romanizer(
            part.processing_text
        )
    elif (
        part.kind
        is JapaneseCorpusPartKind.ASCII_LITERAL
    ):
        result = part.source_text
    elif (
        part.kind
        is JapaneseCorpusPartKind.PUNCTUATION
    ):
        result = canonicalizer(
            part.source_text
        )
    elif (
        part.kind
        is JapaneseCorpusPartKind.HARMONIA_NATIVE
    ):
        result = part.source_text
    elif (
        part.kind
        is JapaneseCorpusPartKind.AMBIGUOUS
    ):
        raise ValueError(
            "ambiguous Japanese corpus part "
            f"cannot be preprocessed: "
            f"{part.source_text!r}"
        )
    else:
        raise ValueError(
            "unsupported Japanese corpus part kind: "
            f"{part.kind!r}"
        )

    if not isinstance(
        result,
        str,
    ):
        raise TypeError(
            "Japanese corpus part processor "
            "output must be a string"
        )

    normalized = normalize_text(
        result
    )

    if not normalized:
        raise ValueError(
            "Japanese corpus part processor "
            "output must not be empty"
        )

    return normalized


def preprocess_structured_japanese_source(
    text: str,
    *,
    part_reader: Callable[
        [str],
        Iterable[JapaneseCorpusPart],
    ],
    romanizer: Callable[[str], str],
    canonicalizer: Callable[[str], str],
) -> str:
    normalized = normalize_japanese_source_text(
        text
    )

    parts = part_reader(
        normalized
    )

    result = "".join(
        preprocess_japanese_corpus_part(
            part,
            romanizer=romanizer,
            canonicalizer=canonicalizer,
        )
        for part in parts
    )

    output = normalize_text(
        result
    )

    if not output:
        raise ValueError(
            "structured Japanese preprocessing "
            "output must not be empty"
        )

    return output


def preprocess_japanese_source(
    text: str,
    *,
    reader: Callable[[str], str] | None = None,
    romanizer: Callable[[str], str] | None = None,
) -> str:
    normalized = normalize_japanese_source_text(
        text
    )

    if reader is None:
        return normalized

    raw_reader_output = reader(normalized)

    if not isinstance(
        raw_reader_output,
        str,
    ):
        raise TypeError(
            "reader output must be a string"
        )

    reader_output = normalize_text(
        raw_reader_output
    )

    if not reader_output:
        raise ValueError(
            "reader output must not be empty"
        )

    if romanizer is None:
        return reader_output

    raw_romanizer_output = romanizer(
        reader_output
    )

    if not isinstance(
        raw_romanizer_output,
        str,
    ):
        raise TypeError(
            "romanizer output must be a string"
        )

    romanizer_output = normalize_text(
        raw_romanizer_output
    )

    if not romanizer_output:
        raise ValueError(
            "romanizer output must not be empty"
        )

    return romanizer_output
