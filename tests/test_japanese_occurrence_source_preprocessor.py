from __future__ import annotations

import pytest

from corpus_builder.japanese_corpus_occurrence import (
    JapaneseCorpusOccurrence,
)
from corpus_builder.japanese_corpus_part import (
    JapaneseCorpusPart,
    JapaneseCorpusPartKind,
)
from corpus_builder.japanese_keystroke_canonicalizer import (
    canonicalize_japanese_keystroke_text,
)
from corpus_builder.japanese_preprocessor import (
    preprocess_occurrence_aware_japanese_source,
)
from corpus_builder.japanese_romanizer import (
    romanize_japanese_reading,
)


def _occurrence(
    *,
    kind: JapaneseCorpusPartKind,
    source_text: str,
    processing_text: str,
    start: int,
) -> JapaneseCorpusOccurrence:
    return JapaneseCorpusOccurrence(
        part=JapaneseCorpusPart(
            kind=kind,
            source_text=source_text,
            processing_text=processing_text,
        ),
        source_start=start,
        source_end=start + len(source_text),
    )


def test_occurrence_aware_source_preprocessing_excludes_kaomoji_region() -> None:
    received: list[str] = []

    def occurrence_reader(
        text: str,
    ) -> tuple[JapaneseCorpusOccurrence, ...]:
        received.append(text)

        return (
            _occurrence(
                kind=JapaneseCorpusPartKind.ASCII_LITERAL,
                source_text="A",
                processing_text="A",
                start=0,
            ),
            _occurrence(
                kind=JapaneseCorpusPartKind.PUNCTUATION,
                source_text="(",
                processing_text="(",
                start=1,
            ),
            _occurrence(
                kind=JapaneseCorpusPartKind.AMBIGUOUS,
                source_text="^",
                processing_text="^",
                start=2,
            ),
            _occurrence(
                kind=JapaneseCorpusPartKind.AMBIGUOUS,
                source_text="○",
                processing_text="マル",
                start=3,
            ),
            _occurrence(
                kind=JapaneseCorpusPartKind.AMBIGUOUS,
                source_text="^",
                processing_text="^",
                start=4,
            ),
            _occurrence(
                kind=JapaneseCorpusPartKind.PUNCTUATION,
                source_text=")",
                processing_text=")",
                start=5,
            ),
            _occurrence(
                kind=JapaneseCorpusPartKind.ASCII_LITERAL,
                source_text="B",
                processing_text="B",
                start=6,
            ),
        )

    result = preprocess_occurrence_aware_japanese_source(
        "  Ａ(^○^)Ｂ  ",
        occurrence_reader=occurrence_reader,
        romanizer=romanize_japanese_reading,
        canonicalizer=canonicalize_japanese_keystroke_text,
    )

    assert received == [
        "A(^○^)B"
    ]
    assert result == "AB"


def test_occurrence_aware_source_preprocessing_returns_none_when_fully_excluded() -> None:
    def occurrence_reader(
        text: str,
    ) -> tuple[JapaneseCorpusOccurrence, ...]:
        assert text == "(^○^)"

        return (
            _occurrence(
                kind=JapaneseCorpusPartKind.PUNCTUATION,
                source_text="(",
                processing_text="(",
                start=0,
            ),
            _occurrence(
                kind=JapaneseCorpusPartKind.AMBIGUOUS,
                source_text="^",
                processing_text="^",
                start=1,
            ),
            _occurrence(
                kind=JapaneseCorpusPartKind.AMBIGUOUS,
                source_text="○",
                processing_text="マル",
                start=2,
            ),
            _occurrence(
                kind=JapaneseCorpusPartKind.AMBIGUOUS,
                source_text="^",
                processing_text="^",
                start=3,
            ),
            _occurrence(
                kind=JapaneseCorpusPartKind.PUNCTUATION,
                source_text=")",
                processing_text=")",
                start=4,
            ),
        )

    assert (
        preprocess_occurrence_aware_japanese_source(
            "(^○^)",
            occurrence_reader=occurrence_reader,
            romanizer=romanize_japanese_reading,
            canonicalizer=canonicalize_japanese_keystroke_text,
        )
        is None
    )


def test_occurrence_aware_source_preprocessing_rejects_empty_reader_output() -> None:
    with pytest.raises(
        ValueError,
        match="requires at least one occurrence",
    ):
        preprocess_occurrence_aware_japanese_source(
            "テスト",
            occurrence_reader=lambda text: (),
            romanizer=romanize_japanese_reading,
            canonicalizer=canonicalize_japanese_keystroke_text,
        )


def test_occurrence_aware_source_preprocessing_keeps_unresolved_ambiguity_error() -> None:
    def occurrence_reader(
        text: str,
    ) -> tuple[JapaneseCorpusOccurrence, ...]:
        assert text == "正解は○です。"

        return (
            _occurrence(
                kind=JapaneseCorpusPartKind.AMBIGUOUS,
                source_text="○",
                processing_text="マル",
                start=3,
            ),
        )

    with pytest.raises(
        ValueError,
        match="ambiguous Japanese corpus part",
    ):
        preprocess_occurrence_aware_japanese_source(
            "正解は○です。",
            occurrence_reader=occurrence_reader,
            romanizer=romanize_japanese_reading,
            canonicalizer=canonicalize_japanese_keystroke_text,
        )
