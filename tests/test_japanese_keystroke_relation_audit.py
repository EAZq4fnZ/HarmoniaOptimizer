from corpus_builder.japanese_corpus_part import (
    JapaneseCorpusPartKind,
)
from corpus_builder.japanese_keystroke_ambiguity import (
    JapaneseKeystrokeAmbiguityClass,
)
from corpus_builder.japanese_keystroke_audit import (
    JapaneseKeystrokeAuditIssue,
    JapaneseKeystrokeAuditResult,
)
from corpus_builder.japanese_keystroke_relation_audit import (
    JapaneseAmbiguityRelationCount,
    JapaneseKeystrokeRelationAuditResult,
    JapaneseSourceProcessingRelationCount,
    summarize_japanese_keystroke_relations,
)
from corpus_builder.japanese_source_processing_relation import (
    JapaneseSourceProcessingRelation,
)


def _make_issue(
    *,
    source_text: str,
    processing_text: str,
    count: int,
) -> JapaneseKeystrokeAuditIssue:
    return JapaneseKeystrokeAuditIssue(
        source_text=source_text,
        processing_text=processing_text,
        kind=JapaneseCorpusPartKind.AMBIGUOUS,
        context="test context",
        reason="test reason",
        count=count,
    )


def test_summarize_japanese_keystroke_relations(
) -> None:
    audit_result = JapaneseKeystrokeAuditResult(
        total_parts=100,
        ambiguous_parts=11,
        issues=(
            _make_issue(
                source_text="\u03b1",
                processing_text="\u03b1",
                count=5,
            ),
            _make_issue(
                source_text="\u03b1",
                processing_text=(
                    "\u30a2\u30eb\u30d5"
                    "\u30a1\u30fc"
                ),
                count=2,
            ),
            _make_issue(
                source_text="\u00b4",
                processing_text=" ",
                count=3,
            ),
            _make_issue(
                source_text="\uff01",
                processing_text="!",
                count=1,
            ),
        ),
    )

    result = (
        summarize_japanese_keystroke_relations(
            audit_result
        )
    )

    assert result == JapaneseKeystrokeRelationAuditResult(
        total_parts=100,
        ambiguous_parts=11,
        relation_counts=(
            JapaneseSourceProcessingRelationCount(
                relation=(
                    JapaneseSourceProcessingRelation
                    .IDENTICAL
                ),
                count=5,
                unique_issue_count=1,
            ),
            JapaneseSourceProcessingRelationCount(
                relation=(
                    JapaneseSourceProcessingRelation
                    .CANONICALIZED
                ),
                count=1,
                unique_issue_count=1,
            ),
            JapaneseSourceProcessingRelationCount(
                relation=(
                    JapaneseSourceProcessingRelation
                    .LINGUISTIC_READING
                ),
                count=2,
                unique_issue_count=1,
            ),
            JapaneseSourceProcessingRelationCount(
                relation=(
                    JapaneseSourceProcessingRelation
                    .LOSSY
                ),
                count=3,
                unique_issue_count=1,
            ),
        ),
        ambiguity_relation_counts=(
            JapaneseAmbiguityRelationCount(
                ambiguity_class=(
                    JapaneseKeystrokeAmbiguityClass
                    .SEMANTIC_SYMBOL
                ),
                relation=(
                    JapaneseSourceProcessingRelation
                    .IDENTICAL
                ),
                count=5,
                unique_issue_count=1,
            ),
            JapaneseAmbiguityRelationCount(
                ambiguity_class=(
                    JapaneseKeystrokeAmbiguityClass
                    .SEMANTIC_SYMBOL
                ),
                relation=(
                    JapaneseSourceProcessingRelation
                    .LINGUISTIC_READING
                ),
                count=2,
                unique_issue_count=1,
            ),
            JapaneseAmbiguityRelationCount(
                ambiguity_class=(
                    JapaneseKeystrokeAmbiguityClass
                    .TYPOGRAPHIC
                ),
                relation=(
                    JapaneseSourceProcessingRelation
                    .LOSSY
                ),
                count=3,
                unique_issue_count=1,
            ),
            JapaneseAmbiguityRelationCount(
                ambiguity_class=(
                    JapaneseKeystrokeAmbiguityClass
                    .OTHER
                ),
                relation=(
                    JapaneseSourceProcessingRelation
                    .CANONICALIZED
                ),
                count=1,
                unique_issue_count=1,
            ),
        ),
    )


def test_summarize_aggregates_duplicate_cross_class_relation(
) -> None:
    audit_result = JapaneseKeystrokeAuditResult(
        total_parts=20,
        ambiguous_parts=7,
        issues=(
            _make_issue(
                source_text="\u03b1",
                processing_text=(
                    "\u30a2\u30eb\u30d5"
                    "\u30a1\u30fc"
                ),
                count=2,
            ),
            _make_issue(
                source_text="\u03b2",
                processing_text=(
                    "\u30d9\u30fc\u30bf"
                ),
                count=5,
            ),
        ),
    )

    result = (
        summarize_japanese_keystroke_relations(
            audit_result
        )
    )

    assert result.relation_counts == (
        JapaneseSourceProcessingRelationCount(
            relation=(
                JapaneseSourceProcessingRelation
                .LINGUISTIC_READING
            ),
            count=7,
            unique_issue_count=2,
        ),
    )

    assert result.ambiguity_relation_counts == (
        JapaneseAmbiguityRelationCount(
            ambiguity_class=(
                JapaneseKeystrokeAmbiguityClass
                .SEMANTIC_SYMBOL
            ),
            relation=(
                JapaneseSourceProcessingRelation
                .LINGUISTIC_READING
            ),
            count=7,
            unique_issue_count=2,
        ),
    )


def test_summarize_empty_audit_result(
) -> None:
    audit_result = JapaneseKeystrokeAuditResult(
        total_parts=0,
        ambiguous_parts=0,
        issues=(),
    )

    result = (
        summarize_japanese_keystroke_relations(
            audit_result
        )
    )

    assert result == JapaneseKeystrokeRelationAuditResult(
        total_parts=0,
        ambiguous_parts=0,
        relation_counts=(),
        ambiguity_relation_counts=(),
    )
