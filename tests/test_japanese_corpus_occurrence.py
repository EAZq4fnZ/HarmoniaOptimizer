from dataclasses import FrozenInstanceError

import pytest

from corpus_builder.japanese_corpus_occurrence import (
    JapaneseCorpusOccurrence,
)
from corpus_builder.japanese_corpus_part import (
    JapaneseCorpusPart,
    JapaneseCorpusPartKind,
)


def make_part(
    source_text: str = "今日",
) -> JapaneseCorpusPart:
    return JapaneseCorpusPart(
        kind=JapaneseCorpusPartKind.JAPANESE_LEXICAL,
        source_text=source_text,
        processing_text="キョウ",
    )


def test_occurrence_preserves_part_and_source_span(
) -> None:
    part = make_part()

    occurrence = JapaneseCorpusOccurrence(
        part=part,
        source_start=3,
        source_end=5,
    )

    assert occurrence.part is part
    assert occurrence.source_start == 3
    assert occurrence.source_end == 5


def test_occurrence_validates_matching_source_span(
) -> None:
    occurrence = JapaneseCorpusOccurrence(
        part=make_part(),
        source_start=3,
        source_end=5,
    )

    occurrence.validate_source(
        "昨日は今日です"
    )


def test_occurrence_rejects_negative_source_start(
) -> None:
    with pytest.raises(
        ValueError,
        match="source_start must not be negative",
    ):
        JapaneseCorpusOccurrence(
            part=make_part(),
            source_start=-1,
            source_end=1,
        )


def test_occurrence_rejects_reversed_source_span(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "source_end must not be less "
            "than source_start"
        ),
    ):
        JapaneseCorpusOccurrence(
            part=make_part(),
            source_start=5,
            source_end=3,
        )


def test_occurrence_rejects_source_end_beyond_text(
) -> None:
    occurrence = JapaneseCorpusOccurrence(
        part=make_part(),
        source_start=3,
        source_end=20,
    )

    with pytest.raises(
        ValueError,
        match="source_end exceeds source text length",
    ):
        occurrence.validate_source(
            "昨日は今日です"
        )


def test_occurrence_rejects_non_matching_source_span(
) -> None:
    occurrence = JapaneseCorpusOccurrence(
        part=make_part(),
        source_start=0,
        source_end=2,
    )

    with pytest.raises(
        ValueError,
        match=(
            "source span does not match "
            "part source_text"
        ),
    ):
        occurrence.validate_source(
            "昨日は今日です"
        )


def test_occurrence_supports_empty_source_span(
) -> None:
    part = JapaneseCorpusPart(
        kind=JapaneseCorpusPartKind.PUNCTUATION,
        source_text="",
        processing_text="．",
    )

    occurrence = JapaneseCorpusOccurrence(
        part=part,
        source_start=2,
        source_end=2,
    )

    occurrence.validate_source(
        "日本語"
    )


def test_occurrence_is_immutable(
) -> None:
    occurrence = JapaneseCorpusOccurrence(
        part=make_part(),
        source_start=3,
        source_end=5,
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        occurrence.source_start = 4  # type: ignore[misc]
