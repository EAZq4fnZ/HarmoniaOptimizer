import pytest

from corpus_builder.japanese_corpus_builder import (
    build_japanese_corpus,
)


def test_build_japanese_corpus_builds_processed_result() -> None:
    result = build_japanese_corpus(
        (
            "今日は晴れです。",
            "明日も晴れです。",
        ),
        reader=lambda text: text,
        romanizer=lambda text: "abc",
    )

    assert result.category == "japanese"
    assert result.source_document_count == 2
    assert result.text == "abc abc"
    assert result.ascii_letter_count == 6


def test_build_japanese_corpus_rejects_empty_documents() -> None:
    with pytest.raises(
        ValueError,
        match="documents must not be empty",
    ):
        build_japanese_corpus(
            (),
            reader=lambda text: text,
            romanizer=lambda text: "abc",
        )


def test_build_japanese_corpus_rejects_empty_document() -> None:
    with pytest.raises(
        ValueError,
        match="document must not be empty",
    ):
        build_japanese_corpus(
            (
                "今日は晴れです。",
                "",
            ),
            reader=lambda text: text,
            romanizer=lambda text: "abc",
        )

def test_build_japanese_corpus_with_default_japanese_pipeline() -> None:
    from corpus_builder.japanese_reader import (
        make_default_japanese_reader,
    )
    from corpus_builder.japanese_romanizer import (
        romanize_japanese_reading,
    )

    result = build_japanese_corpus(
        (
            "今日は晴れです。",
            "明日も晴れです。",
        ),
        reader=make_default_japanese_reader(),
        romanizer=romanize_japanese_reading,
    )

    assert result.category == "japanese"
    assert result.source_document_count == 2
    assert result.ascii_letter_count > 0
    assert result.text
