from __future__ import annotations

from collections.abc import Callable

from .text_normalizer import (
    normalize_fullwidth_ascii,
    normalize_text,
)


def preprocess_japanese_source(
    text: str,
    *,
    reader: Callable[[str], str] | None = None,
) -> str:
    normalized = normalize_fullwidth_ascii(
        normalize_text(text)
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

    return reader_output
