from corpus_builder.japanese_corpus_occurrence import (
    JapaneseCorpusOccurrence,
)
from corpus_builder.japanese_corpus_part import (
    JapaneseCorpusPart,
    JapaneseCorpusPartKind,
)
from corpus_builder.japanese_keystroke_selection import (
    select_japanese_corpus_occurrences_by_policy,
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


def test_policy_selection_keeps_non_ambiguous_occurrences() -> None:
    source = "日本Python"

    occurrences = (
        _occurrence(
            kind=JapaneseCorpusPartKind.JAPANESE_LEXICAL,
            source_text="日本",
            processing_text="ニホン",
            start=0,
        ),
        _occurrence(
            kind=JapaneseCorpusPartKind.ASCII_LITERAL,
            source_text="Python",
            processing_text="Python",
            start=2,
        ),
    )

    assert (
        select_japanese_corpus_occurrences_by_policy(
            source,
            occurrences,
        )
        == occurrences
    )


def test_policy_selection_keeps_semantic_symbol_without_context() -> None:
    source = "正解は○です。"

    occurrence = _occurrence(
        kind=JapaneseCorpusPartKind.AMBIGUOUS,
        source_text="○",
        processing_text="マル",
        start=3,
    )

    assert select_japanese_corpus_occurrences_by_policy(
        source,
        (occurrence,),
    ) == (
        occurrence,
    )


def test_policy_selection_excludes_structural_kaomoji_region() -> None:
    source = "(^○^)"

    occurrences = (
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
        select_japanese_corpus_occurrences_by_policy(
            source,
            occurrences,
        )
        == ()
    )


def test_policy_selection_keeps_occurrences_outside_kaomoji() -> None:
    source = "A(^○^)B"

    left = _occurrence(
        kind=JapaneseCorpusPartKind.ASCII_LITERAL,
        source_text="A",
        processing_text="A",
        start=0,
    )
    right = _occurrence(
        kind=JapaneseCorpusPartKind.ASCII_LITERAL,
        source_text="B",
        processing_text="B",
        start=6,
    )

    occurrences = (
        left,
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
        right,
    )

    assert (
        select_japanese_corpus_occurrences_by_policy(
            source,
            occurrences,
        )
        == (
            left,
            right,
        )
    )


def test_policy_selection_deduplicates_one_region_from_multiple_targets() -> None:
    source = "(`・∀・´ Ξ `・∀・´)"

    occurrences = (
        _occurrence(
            kind=JapaneseCorpusPartKind.AMBIGUOUS,
            source_text="・",
            processing_text="・",
            start=2,
        ),
        _occurrence(
            kind=JapaneseCorpusPartKind.AMBIGUOUS,
            source_text="∀",
            processing_text="∀",
            start=3,
        ),
        _occurrence(
            kind=JapaneseCorpusPartKind.AMBIGUOUS,
            source_text="・",
            processing_text="・",
            start=4,
        ),
    )

    assert (
        select_japanese_corpus_occurrences_by_policy(
            source,
            occurrences,
        )
        == ()
    )


def test_policy_selection_accepts_empty_occurrences() -> None:
    assert (
        select_japanese_corpus_occurrences_by_policy(
            "",
            (),
        )
        == ()
    )
