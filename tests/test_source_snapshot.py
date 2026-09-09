import pytest

from corpus_builder.source_snapshot import (
    hash_document_snapshot,
)


def test_hash_document_snapshot_is_reproducible() -> None:
    documents = (
        "Hello.",
        "Keyboard layout.",
    )

    first = hash_document_snapshot(
        documents
    )
    second = hash_document_snapshot(
        documents
    )

    assert first == second
    assert len(first) == 64


def test_hash_document_snapshot_changes_when_content_changes() -> None:
    first = hash_document_snapshot(
        (
            "Hello.",
            "Keyboard layout.",
        )
    )
    second = hash_document_snapshot(
        (
            "Hello.",
            "Keyboard layouts.",
        )
    )

    assert first != second


def test_hash_document_snapshot_preserves_document_order() -> None:
    first = hash_document_snapshot(
        (
            "First.",
            "Second.",
        )
    )
    second = hash_document_snapshot(
        (
            "Second.",
            "First.",
        )
    )

    assert first != second


def test_hash_document_snapshot_preserves_document_boundaries() -> None:
    first = hash_document_snapshot(
        (
            "ab",
            "c",
        )
    )
    second = hash_document_snapshot(
        (
            "a",
            "bc",
        )
    )

    assert first != second


def test_hash_document_snapshot_rejects_empty_documents_collection() -> None:
    with pytest.raises(
        ValueError,
        match="documents must not be empty",
    ):
        hash_document_snapshot(
            ()
        )


def test_hash_document_snapshot_rejects_non_string_document() -> None:
    with pytest.raises(
        TypeError,
        match="document must be a string",
    ):
        hash_document_snapshot(
            (
                "Hello.",
                123,
            )
        )
