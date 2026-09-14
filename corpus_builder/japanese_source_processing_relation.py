from __future__ import annotations

from enum import Enum

from corpus_builder.japanese_keystroke_canonicalizer import (
    canonicalize_japanese_keystroke_text,
)


class JapaneseSourceProcessingRelation(str, Enum):
    """Relationship between source text and Sudachi processing text."""

    IDENTICAL = "identical"
    CANONICALIZED = "canonicalized"
    LINGUISTIC_READING = "linguistic_reading"
    LOSSY = "lossy"
    UNRESOLVED = "unresolved"


def classify_japanese_source_processing_relation(
    source_text: str,
    processing_text: str,
) -> JapaneseSourceProcessingRelation:
    """Classify how processing text relates to the original source text.

    This relation describes an observed transformation only. It does not
    decide the Harmonia keystroke policy for the text.
    """
    if source_text == processing_text:
        return JapaneseSourceProcessingRelation.IDENTICAL

    canonicalized_source = (
        canonicalize_japanese_keystroke_text(
            source_text
        )
    )

    if (
        canonicalized_source != source_text
        and canonicalized_source
        == processing_text
    ):
        return (
            JapaneseSourceProcessingRelation
            .CANONICALIZED
        )

    if (
        source_text.strip()
        and not processing_text.strip()
    ):
        return JapaneseSourceProcessingRelation.LOSSY

    if _contains_japanese_reading_character(
        processing_text
    ):
        return (
            JapaneseSourceProcessingRelation
            .LINGUISTIC_READING
        )

    return JapaneseSourceProcessingRelation.UNRESOLVED


def _contains_japanese_reading_character(
    text: str,
) -> bool:
    return any(
        _is_japanese_reading_character(
            character
        )
        for character in text
    )


def _is_japanese_reading_character(
    character: str,
) -> bool:
    code_point = ord(character)

    return (
        0x3040 <= code_point <= 0x309F
        or 0x30A0 <= code_point <= 0x30FF
        or 0x31F0 <= code_point <= 0x31FF
    )
