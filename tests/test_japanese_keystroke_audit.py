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


def test_audit_japanese_keystroke_source_uses_shared_source_normalization() -> None:
    from corpus_builder.japanese_keystroke_audit import (
        audit_japanese_keystroke_source,
    )

    received: list[str] = []

    def fake_part_reader(
        text: str,
    ) -> tuple[JapaneseCorpusPart, ...]:
        received.append(text)

        return (
            JapaneseCorpusPart(
                kind=(
                    JapaneseCorpusPartKind.ASCII_LITERAL
                ),
                source_text="ABC123",
                processing_text="ABC123",
            ),
            JapaneseCorpusPart(
                kind=(
                    JapaneseCorpusPartKind.AMBIGUOUS
                ),
                source_text="〜",
                processing_text="ドウ",
            ),
        )

    result = audit_japanese_keystroke_source(
        "  ＡＢＣ１２３\tど〜\n ",
        part_reader=fake_part_reader,
    )

    assert received == [
        "ABC123 ど〜",
    ]

    assert result.total_parts == 2
    assert result.ambiguous_parts == 1
    assert len(result.issues) == 1

    issue = result.issues[0]

    assert issue.source_text == "〜"
    assert issue.processing_text == "ドウ"
    assert issue.context == (
        "  ＡＢＣ１２３\tど〜\n "
    )


def test_audit_japanese_keystroke_source_with_default_reader_records_wave_dash() -> None:
    from corpus_builder.japanese_keystroke_audit import (
        audit_japanese_keystroke_source,
    )
    from corpus_builder.japanese_reader import (
        make_default_japanese_reader,
    )

    reader = make_default_japanese_reader()

    result = audit_japanese_keystroke_source(
        "ど〜",
        part_reader=reader.read_parts,
    )

    assert result.ambiguous_parts == 1
    assert len(result.issues) == 1

    issue = result.issues[0]

    assert issue.source_text == "ど〜"
    assert (
        issue.kind
        is JapaneseCorpusPartKind.AMBIGUOUS
    )
    assert issue.context == "ど〜"


def test_audit_japanese_keystroke_source_accepts_resolved_default_reader_input() -> None:
    from corpus_builder.japanese_keystroke_audit import (
        audit_japanese_keystroke_source,
    )
    from corpus_builder.japanese_reader import (
        make_default_japanese_reader,
    )

    reader = make_default_japanese_reader()

    result = audit_japanese_keystroke_source(
        "今日はPython！〇",
        part_reader=reader.read_parts,
    )

    assert result.total_parts > 0
    assert result.ambiguous_parts == 0
    assert result.issues == ()


def test_merge_japanese_keystroke_audit_results_aggregates_duplicate_issues() -> None:
    from corpus_builder.japanese_keystroke_audit import (
        JapaneseKeystrokeAuditIssue,
        JapaneseKeystrokeAuditResult,
        merge_japanese_keystroke_audit_results,
    )

    issue_first = JapaneseKeystrokeAuditIssue(
        source_text="ど〜",
        processing_text="ドウ",
        kind=JapaneseCorpusPartKind.AMBIGUOUS,
        context="first context",
        reason="ambiguous Japanese keystroke semantics",
        count=2,
    )

    issue_second = JapaneseKeystrokeAuditIssue(
        source_text="ど〜",
        processing_text="ドウ",
        kind=JapaneseCorpusPartKind.AMBIGUOUS,
        context="second context",
        reason="ambiguous Japanese keystroke semantics",
        count=3,
    )

    result = merge_japanese_keystroke_audit_results(
        (
            JapaneseKeystrokeAuditResult(
                total_parts=10,
                ambiguous_parts=2,
                issues=(issue_first,),
            ),
            JapaneseKeystrokeAuditResult(
                total_parts=20,
                ambiguous_parts=3,
                issues=(issue_second,),
            ),
        )
    )

    assert result.total_parts == 30
    assert result.ambiguous_parts == 5
    assert len(result.issues) == 1

    issue = result.issues[0]

    assert issue.count == 5
    assert issue.context == "first context"


def test_audit_japanese_keystroke_sources_aggregates_documents() -> None:
    from corpus_builder.japanese_keystroke_audit import (
        audit_japanese_keystroke_sources,
    )

    def fake_part_reader(
        text: str,
    ) -> tuple[JapaneseCorpusPart, ...]:
        assert text in {
            "first",
            "second",
        }

        return (
            JapaneseCorpusPart(
                kind=(
                    JapaneseCorpusPartKind.AMBIGUOUS
                ),
                source_text="〜",
                processing_text="ドウ",
            ),
        )

    result = audit_japanese_keystroke_sources(
        (
            "first",
            "second",
        ),
        part_reader=fake_part_reader,
    )

    assert result.total_parts == 2
    assert result.ambiguous_parts == 2
    assert len(result.issues) == 1

    issue = result.issues[0]

    assert issue.source_text == "〜"
    assert issue.count == 2
    assert issue.context == "first"


def test_audit_japanese_keystroke_sources_accepts_empty_input() -> None:
    from corpus_builder.japanese_keystroke_audit import (
        audit_japanese_keystroke_sources,
    )

    def fake_part_reader(
        text: str,
    ) -> tuple[JapaneseCorpusPart, ...]:
        raise AssertionError(
            f"unexpected reader call: {text!r}"
        )

    result = audit_japanese_keystroke_sources(
        (),
        part_reader=fake_part_reader,
    )

    assert result.total_parts == 0
    assert result.ambiguous_parts == 0
    assert result.issues == ()
