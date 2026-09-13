from corpus_builder.japanese_corpus_part import (
    JapaneseCorpusPart,
    JapaneseCorpusPartKind,
)
from corpus_builder.japanese_keystroke_audit import (
    audit_japanese_keystroke_parts,
)


def test_audit_japanese_keystroke_parts_accepts_resolved_parts() -> None:
    parts = (
        JapaneseCorpusPart(
            kind=(
                JapaneseCorpusPartKind.JAPANESE_LEXICAL
            ),
            source_text="今日",
            processing_text="キョウ",
        ),
        JapaneseCorpusPart(
            kind=(
                JapaneseCorpusPartKind.ASCII_LITERAL
            ),
            source_text="Python",
            processing_text="Python",
        ),
        JapaneseCorpusPart(
            kind=(
                JapaneseCorpusPartKind.PUNCTUATION
            ),
            source_text="！",
            processing_text="！",
        ),
        JapaneseCorpusPart(
            kind=(
                JapaneseCorpusPartKind.HARMONIA_NATIVE
            ),
            source_text="－",
            processing_text="－",
        ),
    )

    result = audit_japanese_keystroke_parts(
        parts,
        context="今日Python！－",
    )

    assert result.total_parts == 4
    assert result.ambiguous_parts == 0
    assert result.issues == ()


def test_audit_japanese_keystroke_parts_records_ambiguous_part() -> None:
    part = JapaneseCorpusPart(
        kind=JapaneseCorpusPartKind.AMBIGUOUS,
        source_text="〜",
        processing_text="ドウ",
    )

    result = audit_japanese_keystroke_parts(
        (part,),
        context="ど〜",
    )

    assert result.total_parts == 1
    assert result.ambiguous_parts == 1
    assert len(result.issues) == 1

    issue = result.issues[0]

    assert issue.source_text == "〜"
    assert issue.processing_text == "ドウ"
    assert (
        issue.kind
        is JapaneseCorpusPartKind.AMBIGUOUS
    )
    assert issue.context == "ど〜"
    assert issue.reason == (
        "ambiguous Japanese keystroke semantics"
    )
    assert issue.count == 1


def test_audit_japanese_keystroke_parts_aggregates_duplicate_issues() -> None:
    part = JapaneseCorpusPart(
        kind=JapaneseCorpusPartKind.AMBIGUOUS,
        source_text="〜",
        processing_text="ドウ",
    )

    result = audit_japanese_keystroke_parts(
        (
            part,
            part,
            part,
        ),
        context="ど〜〜〜",
    )

    assert result.total_parts == 3
    assert result.ambiguous_parts == 3
    assert len(result.issues) == 1

    issue = result.issues[0]

    assert issue.count == 3
    assert issue.context == "ど〜〜〜"


def test_audit_japanese_keystroke_parts_keeps_distinct_ambiguities() -> None:
    parts = (
        JapaneseCorpusPart(
            kind=JapaneseCorpusPartKind.AMBIGUOUS,
            source_text="α",
            processing_text="アルファー",
        ),
        JapaneseCorpusPart(
            kind=JapaneseCorpusPartKind.AMBIGUOUS,
            source_text="×",
            processing_text="バツ",
        ),
    )

    result = audit_japanese_keystroke_parts(
        parts,
        context="α×",
    )

    assert result.total_parts == 2
    assert result.ambiguous_parts == 2
    assert len(result.issues) == 2

    assert {
        issue.source_text
        for issue in result.issues
    } == {
        "α",
        "×",
    }


def test_audit_japanese_keystroke_parts_accepts_empty_input() -> None:
    result = audit_japanese_keystroke_parts(
        (),
        context="",
    )

    assert result.total_parts == 0
    assert result.ambiguous_parts == 0
    assert result.issues == ()
