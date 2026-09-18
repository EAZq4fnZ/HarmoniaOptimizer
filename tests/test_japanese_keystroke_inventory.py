# tests/test_japanese_keystroke_inventory.py

from collections.abc import Iterable

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
from corpus_builder.japanese_keystroke_context import (
    JapaneseKeystrokeContextEvidence,
)
from corpus_builder.japanese_keystroke_inventory import (
    audit_japanese_keystroke_inventory,
)
from corpus_builder.japanese_source_processing_relation import (
    JapaneseSourceProcessingRelation,
)


def make_occurrence(
    *,
    source_text: str,
    processing_text: str,
    source_start: int,
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
        source_end=(
            source_start + len(source_text)
        ),
    )


def make_occurrence_reader(
    text: str,
) -> Iterable[JapaneseCorpusOccurrence]:
    if text == "○○":
        return (
            make_occurrence(
                source_text="○",
                processing_text="○",
                source_start=0,
            ),
            make_occurrence(
                source_text="○",
                processing_text="○",
                source_start=1,
            ),
        )

    if text == "○":
        return (
            make_occurrence(
                source_text="○",
                processing_text="○",
                source_start=0,
            ),
        )

    if text == "α波":
        return (
            make_occurrence(
                source_text="α",
                processing_text="アルファー",
                source_start=0,
            ),
            make_occurrence(
                source_text="波",
                processing_text="ナミ",
                source_start=1,
                kind=(
                    JapaneseCorpusPartKind.JAPANESE_LEXICAL
                ),
            ),
        )

    if text == (
            "正解は○です。"
            "かなり離れた通常文です。"
            "（^○^）♡"
        ):
        first_start = text.index("○")
        second_start = text.index(
            "○",
            first_start + 1,
        )

        return (
            make_occurrence(
                source_text="○",
                processing_text="○",
                source_start=first_start,
            ),
            make_occurrence(
                source_text="○",
                processing_text="○",
                source_start=second_start,
            ),
        )

    return ()


def test_counts_documents_and_occurrences(
) -> None:
    result = audit_japanese_keystroke_inventory(
        (
            "○○",
            "○",
            "α波",
        ),
        occurrence_reader=make_occurrence_reader,
    )

    assert result.document_count == 3
    assert result.total_occurrences == 5
    assert result.ambiguous_occurrences == 4

    assert (
        sum(
            row.occurrence_count
            for row in result.rows
        )
        == result.ambiguous_occurrences
    )


def test_counts_repeated_issue_once_per_document(
) -> None:
    result = audit_japanese_keystroke_inventory(
        (
            "○○",
            "○",
        ),
        occurrence_reader=make_occurrence_reader,
    )

    assert len(result.rows) == 1

    row = result.rows[0]

    assert row.source_text == "○"
    assert row.processing_text == "○"
    assert row.occurrence_count == 3
    assert row.document_count == 2


def test_preserves_three_axis_semantics(
) -> None:
    result = audit_japanese_keystroke_inventory(
        ("α波",),
        occurrence_reader=make_occurrence_reader,
    )

    assert len(result.rows) == 1

    row = result.rows[0]

    assert (
        row.ambiguity_class
        is JapaneseKeystrokeAmbiguityClass.SEMANTIC_SYMBOL
    )
    assert (
        row.relation
        is JapaneseSourceProcessingRelation.LINGUISTIC_READING
    )
    assert (
        row.evidence
        is JapaneseKeystrokeContextEvidence.NONE
    )


def test_distinguishes_exact_context_evidence(
) -> None:
    result = audit_japanese_keystroke_inventory(
        (
            (
                "正解は○です。"
                "かなり離れた通常文です。"
                "（^○^）♡"
            ),
        ),
        occurrence_reader=make_occurrence_reader,
    )
    rows = {
        row.evidence: row
        for row in result.rows
    }

    assert set(rows) == {
        JapaneseKeystrokeContextEvidence.NONE,
        JapaneseKeystrokeContextEvidence.KAOMOJI_STRUCTURAL,
    }

    assert (
        rows[
            JapaneseKeystrokeContextEvidence.NONE
        ].occurrence_count
        == 1
    )
    assert (
        rows[
            JapaneseKeystrokeContextEvidence.NONE
        ].document_count
        == 1
    )

    assert (
        rows[
            JapaneseKeystrokeContextEvidence.KAOMOJI_STRUCTURAL
        ].occurrence_count
        == 1
    )
    assert (
        rows[
            JapaneseKeystrokeContextEvidence.KAOMOJI_STRUCTURAL
        ].document_count
        == 1
    )


def test_non_ambiguous_occurrences_only_affect_total(
) -> None:
    result = audit_japanese_keystroke_inventory(
        ("α波",),
        occurrence_reader=make_occurrence_reader,
    )

    assert result.document_count == 1
    assert result.total_occurrences == 2
    assert result.ambiguous_occurrences == 1
    assert len(result.rows) == 1


def test_empty_corpus_produces_empty_inventory(
) -> None:
    result = audit_japanese_keystroke_inventory(
        (),
        occurrence_reader=make_occurrence_reader,
    )

    assert result.document_count == 0
    assert result.total_occurrences == 0
    assert result.ambiguous_occurrences == 0
    assert result.rows == ()


def test_occurrence_reader_receives_normalized_source(
) -> None:
    received_texts: list[str] = []

    def occurrence_reader(
        text: str,
    ) -> Iterable[JapaneseCorpusOccurrence]:
        received_texts.append(text)

        start = text.index("○")

        return (
            make_occurrence(
                source_text="○",
                processing_text="○",
                source_start=start,
            ),
        )

    result = audit_japanese_keystroke_inventory(
        ("Ａ○",),
        occurrence_reader=occurrence_reader,
    )

    assert received_texts == ["A○"]
    assert result.document_count == 1
    assert result.total_occurrences == 1
    assert result.ambiguous_occurrences == 1
    assert len(result.rows) == 1
