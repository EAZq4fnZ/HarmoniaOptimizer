import pytest

from corpus_builder.english_corpus_builder import (
    build_english_corpus,
)


def test_build_english_corpus_builds_processed_result() -> None:
    result = build_english_corpus(
        (
            "Hello WORLD.",
            "Keyboard layout.",
        )
    )

    assert result.category == "english"
    assert result.source_document_count == 2
    assert result.text == "Hello WORLD. Keyboard layout."
    assert result.ascii_letter_count == 24


def test_build_english_corpus_rejects_empty_documents() -> None:
    with pytest.raises(
        ValueError,
        match="documents must not be empty",
    ):
        build_english_corpus(
            ()
        )


def test_build_english_corpus_rejects_empty_document() -> None:
    with pytest.raises(
        ValueError,
        match="document must not be empty",
    ):
        build_english_corpus(
            (
                "Hello.",
                "",
            )
        )

def test_build_english_corpus_normalizes_source_text() -> None:
    result = build_english_corpus(
        (
            "  Ｈｅｌｌｏ\nWORLD.  ",
            "Keyboard\tlayout.",
        )
    )

    assert (
        result.text
        == "Hello WORLD. Keyboard layout."
    )
    assert result.ascii_letter_count == 24


def test_build_english_corpus_rejects_whitespace_only_document() -> None:
    with pytest.raises(
        ValueError,
        match="document must not be empty after normalization",
    ):
        build_english_corpus(
            (
                "Hello.",
                " \n\t ",
            )
        )


def test_build_english_corpus_rejects_document_removed_by_normalization() -> None:
    with pytest.raises(
        ValueError,
        match="document must not be empty after normalization",
    ):
        build_english_corpus(
            (
                "Hello.",
                "\u200b\ufeff",
            )
        )


def test_build_english_corpus_preserves_case_punctuation_and_digits() -> None:
    result = build_english_corpus(
        (
            "Hello, WORLD! 2026",
        )
    )

    assert result.text == "Hello, WORLD! 2026"
    assert result.source_document_count == 1
    assert result.ascii_letter_count == 10


def test_build_english_corpus_accepts_document_generator() -> None:
    documents = (
        document
        for document in (
            "Hello.",
            "Keyboard.",
        )
    )

    result = build_english_corpus(
        documents
    )

    assert result.text == "Hello. Keyboard."
    assert result.source_document_count == 2
