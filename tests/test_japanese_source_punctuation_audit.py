# tests\test_japanese_source_punctuation_audit.py

from corpus_builder.japanese_source_punctuation_audit import (
    JapaneseSourceBracketMismatchCount,
    audit_japanese_source_punctuation,
)


def pair_counts_by_open(
    result,
):
    return {
        row.open_symbol: row
        for row in result.pair_counts
    }


def test_audits_simple_matched_pairs() -> None:
    result = audit_japanese_source_punctuation(
        (
            "これは「引用」です。",
            "『作品名』と【見出し】です。",
        )
    )

    rows = pair_counts_by_open(result)

    assert result.document_count == 2
    assert result.documents_with_brackets == 2

    assert rows["「"].source_open_count == 1
    assert rows["「"].source_close_count == 1
    assert rows["「"].matched_pair_count == 1
    assert rows["「"].unmatched_open_count == 0
    assert rows["「"].unmatched_close_count == 0

    assert rows["『"].matched_pair_count == 1
    assert rows["【"].matched_pair_count == 1

    assert result.mismatched_close_count == 0
    assert result.maximum_strict_stack_depth == 1


def test_tracks_unmatched_open_and_close() -> None:
    result = audit_japanese_source_punctuation(
        (
            "「open only",
            "close only」",
        )
    )

    row = pair_counts_by_open(result)["「"]

    assert row.source_open_count == 1
    assert row.source_close_count == 1
    assert row.matched_pair_count == 0
    assert row.unmatched_open_count == 1
    assert row.unmatched_close_count == 1


def test_tracks_typed_mismatch_without_mutating_stack() -> None:
    result = audit_japanese_source_punctuation(
        ("『wrong close」",)
    )

    rows = pair_counts_by_open(result)

    assert result.mismatched_close_count == 1
    assert result.documents_with_mismatch == 1

    assert result.mismatch_counts == (
        JapaneseSourceBracketMismatchCount(
            close_symbol="」",
            expected_open="「",
            actual_stack_top="『",
            count=1,
            document_count=1,
        ),
    )

    assert rows["『"].source_open_count == 1
    assert rows["『"].unmatched_open_count == 1

    assert rows["「"].source_close_count == 1
    assert rows["「"].unmatched_close_count == 0


def test_counts_nested_matched_pairs() -> None:
    result = audit_japanese_source_punctuation(
        ("「outer『inner』outer」",)
    )

    rows = pair_counts_by_open(result)

    assert rows["「"].matched_pair_count == 1
    assert rows["『"].matched_pair_count == 1

    assert result.nested_matched_pair_count == 1
    assert (
        result.documents_with_nested_matched_pairs
        == 1
    )
    assert result.maximum_strict_stack_depth == 2


def test_stack_depth_is_not_semantic_nesting_claim() -> None:
    result = audit_japanese_source_punctuation(
        ("「first 「second 「third",)
    )

    row = pair_counts_by_open(result)["「"]

    assert row.source_open_count == 3
    assert row.matched_pair_count == 0
    assert row.unmatched_open_count == 3

    assert result.nested_matched_pair_count == 0
    assert result.maximum_strict_stack_depth == 3


def test_resets_stack_for_each_document() -> None:
    result = audit_japanese_source_punctuation(
        (
            "「open",
            "close」",
        )
    )

    row = pair_counts_by_open(result)["「"]

    assert row.matched_pair_count == 0
    assert row.unmatched_open_count == 1
    assert row.unmatched_close_count == 1
    assert result.maximum_strict_stack_depth == 1


def test_tracks_pair_document_count() -> None:
    result = audit_japanese_source_punctuation(
        (
            "「a」「b」",
            "「c」",
            "no brackets",
        )
    )

    row = pair_counts_by_open(result)["「"]

    assert row.matched_pair_count == 3
    assert row.document_count == 2

    assert result.document_count == 3
    assert result.documents_with_brackets == 2


def test_tracks_mismatch_document_count_separately() -> None:
    result = audit_japanese_source_punctuation(
        (
            "『a」 and 『b」",
            "『c」",
        )
    )

    assert result.mismatched_close_count == 3
    assert result.documents_with_mismatch == 2

    assert result.mismatch_counts == (
        JapaneseSourceBracketMismatchCount(
            close_symbol="」",
            expected_open="「",
            actual_stack_top="『",
            count=3,
            document_count=2,
        ),
    )


def test_empty_corpus_returns_zero_counts() -> None:
    result = audit_japanese_source_punctuation(())

    assert result.document_count == 0
    assert result.documents_with_brackets == 0
    assert result.mismatched_close_count == 0
    assert result.documents_with_mismatch == 0
    assert result.nested_matched_pair_count == 0
    assert (
        result.documents_with_nested_matched_pairs
        == 0
    )
    assert result.maximum_strict_stack_depth == 0

    assert all(
        row.source_open_count == 0
        and row.source_close_count == 0
        and row.matched_pair_count == 0
        and row.unmatched_open_count == 0
        and row.unmatched_close_count == 0
        and row.document_count == 0
        for row in result.pair_counts
    )

    assert result.mismatch_counts == ()


def test_ignores_unrelated_punctuation() -> None:
    result = audit_japanese_source_punctuation(
        (
            "（）［］{}<>「ok」",
        )
    )

    row = pair_counts_by_open(result)["「"]

    assert row.source_open_count == 1
    assert row.source_close_count == 1
    assert row.matched_pair_count == 1

    assert sum(
        item.source_open_count
        for item in result.pair_counts
    ) == 1