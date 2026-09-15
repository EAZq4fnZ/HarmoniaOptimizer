from corpus_builder.japanese_corpus_occurrence import (
    JapaneseCorpusOccurrence,
)
from corpus_builder.japanese_corpus_part import (
    JapaneseCorpusPart,
    JapaneseCorpusPartKind,
)
from corpus_builder.japanese_keystroke_ambiguity import (
    JapaneseKeystrokeAmbiguityClass,
)
from corpus_builder.japanese_keystroke_audit import (
    JapaneseKeystrokeAuditIssue,
    JapaneseKeystrokeAuditResult,
)
from corpus_builder.japanese_keystroke_context import (
    JapaneseKeystrokeContextEvidence,
)
from corpus_builder.japanese_keystroke_context_audit import (
    audit_japanese_keystroke_occurrence_contexts,
    summarize_japanese_keystroke_contexts,
)
from corpus_builder.japanese_source_processing_relation import (
    JapaneseSourceProcessingRelation,
)


def make_audit_result(
) -> JapaneseKeystrokeAuditResult:
    return JapaneseKeystrokeAuditResult(
        total_parts=100,
        ambiguous_parts=6,
        issues=(
            JapaneseKeystrokeAuditIssue(
                source_text="○",
                processing_text="○",
                kind=JapaneseCorpusPartKind.AMBIGUOUS,
                context="正解は○です。",
                reason="ambiguous Japanese corpus part",
                count=2,
            ),
            JapaneseKeystrokeAuditIssue(
                source_text="○",
                processing_text="○",
                kind=JapaneseCorpusPartKind.AMBIGUOUS,
                context="（^○^）♡",
                reason="ambiguous Japanese corpus part",
                count=3,
            ),
            JapaneseKeystrokeAuditIssue(
                source_text="α",
                processing_text="アルファー",
                kind=JapaneseCorpusPartKind.AMBIGUOUS,
                context="α波について説明します。",
                reason="ambiguous Japanese corpus part",
                count=1,
            ),
        ),
    )


def test_summarizes_context_evidence_counts(
) -> None:
    result = summarize_japanese_keystroke_contexts(
        make_audit_result()
    )

    counts = {
        row.evidence: row.count
        for row in result.context_counts
    }

    assert counts == {
        JapaneseKeystrokeContextEvidence.NONE: 3,
        JapaneseKeystrokeContextEvidence.KAOMOJI_STRUCTURAL: 3,
    }


def test_preserves_total_and_ambiguous_counts(
) -> None:
    result = summarize_japanese_keystroke_contexts(
        make_audit_result()
    )

    assert result.total_parts == 100
    assert result.ambiguous_parts == 6

    assert (
        sum(
            row.count
            for row in result.context_counts
        )
        == result.ambiguous_parts
    )

    assert (
        sum(
            row.count
            for row in (
                result.ambiguity_relation_context_counts
            )
        )
        == result.ambiguous_parts
    )


def test_tracks_unique_issue_counts(
) -> None:
    result = summarize_japanese_keystroke_contexts(
        make_audit_result()
    )

    unique_counts = {
        row.evidence: row.unique_issue_count
        for row in result.context_counts
    }

    assert unique_counts == {
        JapaneseKeystrokeContextEvidence.NONE: 2,
        JapaneseKeystrokeContextEvidence.KAOMOJI_STRUCTURAL: 1,
    }


def test_builds_three_axis_matrix(
) -> None:
    result = summarize_japanese_keystroke_contexts(
        make_audit_result()
    )

    rows = {
        (
            row.ambiguity_class,
            row.relation,
            row.evidence,
        ): (
            row.count,
            row.unique_issue_count,
        )
        for row in (
            result.ambiguity_relation_context_counts
        )
    }

    assert rows[
        (
            JapaneseKeystrokeAmbiguityClass.SEMANTIC_SYMBOL,
            JapaneseSourceProcessingRelation.IDENTICAL,
            JapaneseKeystrokeContextEvidence.NONE,
        )
    ] == (2, 1)

    assert rows[
        (
            JapaneseKeystrokeAmbiguityClass.SEMANTIC_SYMBOL,
            JapaneseSourceProcessingRelation.IDENTICAL,
            JapaneseKeystrokeContextEvidence.KAOMOJI_STRUCTURAL,
        )
    ] == (3, 1)

    assert rows[
        (
            JapaneseKeystrokeAmbiguityClass.SEMANTIC_SYMBOL,
            JapaneseSourceProcessingRelation.LINGUISTIC_READING,
            JapaneseKeystrokeContextEvidence.NONE,
        )
    ] == (1, 1)


def test_context_evidence_does_not_resolve_policy(
) -> None:
    result = summarize_japanese_keystroke_contexts(
        make_audit_result()
    )

    structural_rows = tuple(
        row
        for row in (
            result.ambiguity_relation_context_counts
        )
        if (
            row.evidence
            is JapaneseKeystrokeContextEvidence.KAOMOJI_STRUCTURAL
        )
    )

    assert len(structural_rows) == 1
    assert structural_rows[0].count == 3


def make_occurrence(
    *,
    source_text: str,
    processing_text: str,
    source_start: int,
    source_end: int,
    kind: JapaneseCorpusPartKind = (
        JapaneseCorpusPartKind.AMBIGUOUS
    ),
) -> JapaneseCorpusOccurrence:
    return JapaneseCorpusOccurrence(
        part=JapaneseCorpusPart(
            kind=kind,
            source_text=source_text,
            processing_text=processing_text,
        ),
        source_start=source_start,
        source_end=source_end,
    )


def test_occurrence_audit_distinguishes_repeated_source_contexts(
) -> None:
    source = (
        "正解は○です。"
        "かなり離れた通常文です。"
        "（^○^）♡"
    )

    first_start = source.index(
        "○"
    )
    second_start = source.index(
        "○",
        first_start + 1,
    )

    occurrences = (
        make_occurrence(
            source_text="○",
            processing_text="○",
            source_start=first_start,
            source_end=first_start + 1,
        ),
        make_occurrence(
            source_text="○",
            processing_text="○",
            source_start=second_start,
            source_end=second_start + 1,
        ),
    )

    result = (
        audit_japanese_keystroke_occurrence_contexts(
            source,
            occurrences,
        )
    )

    counts = {
        row.evidence: row.count
        for row in result.context_counts
    }

    assert counts == {
        JapaneseKeystrokeContextEvidence.NONE: 1,
        JapaneseKeystrokeContextEvidence.KAOMOJI_STRUCTURAL: 1,
    }


def test_occurrence_audit_preserves_exact_totals(
) -> None:
    source = "α波と○です。"

    alpha_start = source.index(
        "α"
    )
    circle_start = source.index(
        "○"
    )

    occurrences = (
        make_occurrence(
            source_text="α",
            processing_text="アルファー",
            source_start=alpha_start,
            source_end=alpha_start + 1,
        ),
        make_occurrence(
            source_text="波",
            processing_text="ナミ",
            source_start=1,
            source_end=2,
            kind=JapaneseCorpusPartKind.JAPANESE_LEXICAL,
        ),
        make_occurrence(
            source_text="○",
            processing_text="○",
            source_start=circle_start,
            source_end=circle_start + 1,
        ),
    )

    result = (
        audit_japanese_keystroke_occurrence_contexts(
            source,
            occurrences,
        )
    )

    assert result.total_parts == 3
    assert result.ambiguous_parts == 2

    assert (
        sum(
            row.count
            for row in result.context_counts
        )
        == 2
    )

    assert (
        sum(
            row.count
            for row in (
                result.ambiguity_relation_context_counts
            )
        )
        == 2
    )


def test_occurrence_audit_builds_exact_three_axis_matrix(
) -> None:
    source = (
        "α波について説明します。"
        "十分に離れた通常の文章です。"
        "（^○^）♡"
    )

    alpha_start = source.index(
        "α"
    )
    circle_start = source.index(
        "○"
    )

    occurrences = (
        make_occurrence(
            source_text="α",
            processing_text="アルファー",
            source_start=alpha_start,
            source_end=alpha_start + 1,
        ),
        make_occurrence(
            source_text="○",
            processing_text="○",
            source_start=circle_start,
            source_end=circle_start + 1,
        ),
    )

    result = (
        audit_japanese_keystroke_occurrence_contexts(
            source,
            occurrences,
        )
    )

    rows = {
        (
            row.ambiguity_class,
            row.relation,
            row.evidence,
        ): row.count
        for row in (
            result.ambiguity_relation_context_counts
        )
    }

    assert rows[
        (
            JapaneseKeystrokeAmbiguityClass.SEMANTIC_SYMBOL,
            JapaneseSourceProcessingRelation.LINGUISTIC_READING,
            JapaneseKeystrokeContextEvidence.NONE,
        )
    ] == 1

    assert rows[
        (
            JapaneseKeystrokeAmbiguityClass.SEMANTIC_SYMBOL,
            JapaneseSourceProcessingRelation.IDENTICAL,
            JapaneseKeystrokeContextEvidence.KAOMOJI_STRUCTURAL,
        )
    ] == 1


def test_occurrence_audit_tracks_unique_semantic_issues(
) -> None:
    source = "○です。離れた文章です。○です。"

    first_start = source.index(
        "○"
    )
    second_start = source.index(
        "○",
        first_start + 1,
    )

    occurrences = (
        make_occurrence(
            source_text="○",
            processing_text="○",
            source_start=first_start,
            source_end=first_start + 1,
        ),
        make_occurrence(
            source_text="○",
            processing_text="○",
            source_start=second_start,
            source_end=second_start + 1,
        ),
    )

    result = (
        audit_japanese_keystroke_occurrence_contexts(
            source,
            occurrences,
        )
    )

    assert len(
        result.context_counts
    ) == 1

    row = result.context_counts[0]

    assert row.count == 2
    assert row.unique_issue_count == 1
