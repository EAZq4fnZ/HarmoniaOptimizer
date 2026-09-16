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
    preprocess_japanese_corpus_occurrences,
)
from corpus_builder.japanese_romanizer import (
    romanize_japanese_reading,
)


def make_occurrence(
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


def test_preprocess_japanese_corpus_occurrences_joins_selected_parts() -> None:
    occurrences = (
        make_occurrence(
            kind=JapaneseCorpusPartKind.JAPANESE_LEXICAL,
            source_text="今日",
            processing_text="キョウ",
            start=0,
        ),
        make_occurrence(
            kind=JapaneseCorpusPartKind.ASCII_LITERAL,
            source_text="Python",
            processing_text="パイソン",
            start=2,
        ),
        make_occurrence(
            kind=JapaneseCorpusPartKind.PUNCTUATION,
            source_text="！",
            processing_text="！",
            start=8,
        ),
        make_occurrence(
            kind=JapaneseCorpusPartKind.HARMONIA_NATIVE,
            source_text="－",
            processing_text="－",
            start=9,
        ),
        make_occurrence(
            kind=JapaneseCorpusPartKind.JAPANESE_LEXICAL,
            source_text="〇",
            processing_text="〇",
            start=10,
        ),
    )

    assert preprocess_japanese_corpus_occurrences(
        occurrences,
        romanizer=romanize_japanese_reading,
        canonicalizer=canonicalize_japanese_keystroke_text,
    ) == "kyouPython!－maru"


def test_preprocess_japanese_corpus_occurrences_accepts_iterable() -> None:
    occurrence = make_occurrence(
        kind=JapaneseCorpusPartKind.ASCII_LITERAL,
        source_text="Python",
        processing_text="Python",
        start=0,
    )

    def generate():
        yield occurrence

    assert preprocess_japanese_corpus_occurrences(
        generate(),
        romanizer=romanize_japanese_reading,
        canonicalizer=canonicalize_japanese_keystroke_text,
    ) == "Python"


def test_preprocess_japanese_corpus_occurrences_rejects_ambiguous_part() -> None:
    occurrence = make_occurrence(
        kind=JapaneseCorpusPartKind.AMBIGUOUS,
        source_text="〜",
        processing_text="ドウ",
        start=0,
    )

    with pytest.raises(
        ValueError,
        match="ambiguous Japanese corpus part",
    ):
        preprocess_japanese_corpus_occurrences(
            (occurrence,),
            romanizer=romanize_japanese_reading,
            canonicalizer=canonicalize_japanese_keystroke_text,
        )


def test_preprocess_japanese_corpus_occurrences_rejects_empty_input() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Japanese corpus occurrence preprocessing "
            "output must not be empty"
        ),
    ):
        preprocess_japanese_corpus_occurrences(
            (),
            romanizer=romanize_japanese_reading,
            canonicalizer=canonicalize_japanese_keystroke_text,
        )
