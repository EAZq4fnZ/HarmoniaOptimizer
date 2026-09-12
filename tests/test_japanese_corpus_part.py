from dataclasses import FrozenInstanceError

import pytest

from corpus_builder.japanese_corpus_part import (
    JapaneseCorpusPart,
    JapaneseCorpusPartKind,
)


def test_japanese_corpus_part_kinds_are_stable() -> None:
    assert tuple(JapaneseCorpusPartKind) == (
        JapaneseCorpusPartKind.JAPANESE_LEXICAL,
        JapaneseCorpusPartKind.ASCII_LITERAL,
        JapaneseCorpusPartKind.PUNCTUATION,
        JapaneseCorpusPartKind.HARMONIA_NATIVE,
        JapaneseCorpusPartKind.AMBIGUOUS,
    )

    assert (
        JapaneseCorpusPartKind.JAPANESE_LEXICAL.value
        == "japanese_lexical"
    )
    assert (
        JapaneseCorpusPartKind.ASCII_LITERAL.value
        == "ascii_literal"
    )
    assert (
        JapaneseCorpusPartKind.PUNCTUATION.value
        == "punctuation"
    )
    assert (
        JapaneseCorpusPartKind.HARMONIA_NATIVE.value
        == "harmonia_native"
    )
    assert (
        JapaneseCorpusPartKind.AMBIGUOUS.value
        == "ambiguous"
    )


def test_japanese_lexical_part_preserves_source_and_processing_text() -> None:
    part = JapaneseCorpusPart(
        kind=JapaneseCorpusPartKind.JAPANESE_LEXICAL,
        source_text="今日",
        processing_text="キョウ",
    )

    assert part.kind is JapaneseCorpusPartKind.JAPANESE_LEXICAL
    assert part.source_text == "今日"
    assert part.processing_text == "キョウ"


def test_ascii_literal_part_preserves_literal_text() -> None:
    part = JapaneseCorpusPart(
        kind=JapaneseCorpusPartKind.ASCII_LITERAL,
        source_text="Python",
        processing_text="Python",
    )

    assert part.kind is JapaneseCorpusPartKind.ASCII_LITERAL
    assert part.source_text == "Python"
    assert part.processing_text == "Python"


def test_punctuation_part_preserves_source_before_canonicalization() -> None:
    part = JapaneseCorpusPart(
        kind=JapaneseCorpusPartKind.PUNCTUATION,
        source_text="！",
        processing_text="！",
    )

    assert part.kind is JapaneseCorpusPartKind.PUNCTUATION
    assert part.source_text == "！"
    assert part.processing_text == "！"


def test_harmonia_native_part_preserves_native_character() -> None:
    part = JapaneseCorpusPart(
        kind=JapaneseCorpusPartKind.HARMONIA_NATIVE,
        source_text="、",
        processing_text="、",
    )

    assert part.kind is JapaneseCorpusPartKind.HARMONIA_NATIVE
    assert part.source_text == "、"
    assert part.processing_text == "、"


def test_ambiguous_part_retains_original_input() -> None:
    part = JapaneseCorpusPart(
        kind=JapaneseCorpusPartKind.AMBIGUOUS,
        source_text="〜",
        processing_text="〜",
    )

    assert part.kind is JapaneseCorpusPartKind.AMBIGUOUS
    assert part.source_text == "〜"
    assert part.processing_text == "〜"


def test_part_can_represent_empty_sudachi_surface() -> None:
    part = JapaneseCorpusPart(
        kind=JapaneseCorpusPartKind.PUNCTUATION,
        source_text="",
        processing_text="．",
    )

    assert part.source_text == ""
    assert part.processing_text == "．"


def test_japanese_corpus_part_is_immutable() -> None:
    part = JapaneseCorpusPart(
        kind=JapaneseCorpusPartKind.JAPANESE_LEXICAL,
        source_text="日本",
        processing_text="ニホン",
    )

    with pytest.raises(FrozenInstanceError):
        part.processing_text = "ニッポン"  # type: ignore[misc]
