import pytest

from corpus_builder.japanese_corpus_part import (
    JapaneseCorpusPart,
    JapaneseCorpusPartKind,
)
from corpus_builder.japanese_reader import (
    JapaneseReader,
    make_default_japanese_reader,
)
from corpus_builder.sudachi_reader import make_default_sudachi_tokenizer


def test_japanese_reader_joins_token_readings() -> None:
    def fake_tokenizer(
        text: str,
    ) -> tuple[str, ...]:
        assert text == "今日は良い天気です"
        return (
            "キョウ",
            "ハ",
            "ヨイ",
            "テンキ",
            "デス",
        )

    reader = JapaneseReader(
        tokenizer=fake_tokenizer
    )

    assert reader(
        "今日は良い天気です"
    ) == "キョウハヨイテンキデス"


def test_japanese_reader_accepts_iterable_token_readings() -> None:
    def fake_tokenizer(
        text: str,
    ):
        assert text == "日本語"
        yield "ニホン"
        yield "ゴ"

    reader = JapaneseReader(
        tokenizer=fake_tokenizer
    )

    assert reader(
        "日本語"
    ) == "ニホンゴ"


def test_japanese_reader_with_default_sudachi_tokenizer() -> None:
    reader = JapaneseReader(
        tokenizer=make_default_sudachi_tokenizer()
    )

    assert reader(
        "今日は良い天気です"
    ) == "キョウハヨイテンキデス"


def test_make_default_japanese_reader_uses_default_sudachi_tokenizer() -> None:
    reader = make_default_japanese_reader()

    assert reader(
        "今日は良い天気です"
    ) == "キョウハヨイテンキデス"

def test_japanese_reader_read_parts_returns_structured_parts() -> None:
    def fake_tokenizer(
        text: str,
    ) -> tuple[str, ...]:
        assert text == "今日Python"
        return (
            "キョウ",
            "Python",
        )

    def fake_part_tokenizer(
        text: str,
    ) -> tuple[JapaneseCorpusPart, ...]:
        assert text == "今日Python"

        return (
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
        )

    reader = JapaneseReader(
        tokenizer=fake_tokenizer,
        part_tokenizer=fake_part_tokenizer,
    )

    assert reader(
        "今日Python"
    ) == "キョウPython"

    assert reader.read_parts(
        "今日Python"
    ) == (
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
    )


def test_japanese_reader_read_parts_requires_structured_tokenizer() -> None:
    reader = JapaneseReader(
        tokenizer=lambda text: (text,)
    )

    with pytest.raises(
        RuntimeError,
        match="does not have a structured tokenizer",
    ):
        reader.read_parts(
            "日本語"
        )


def test_make_default_japanese_reader_supports_structured_parts() -> None:
    reader = make_default_japanese_reader()

    parts = reader.read_parts(
        "〇"
    )

    assert len(parts) == 1

    part = parts[0]

    assert (
        part.kind
        is JapaneseCorpusPartKind.JAPANESE_LEXICAL
    )
    assert part.source_text == "〇"
    assert part.processing_text == "〇"

def test_japanese_reader_read_occurrences_returns_exact_occurrences() -> None:
    from corpus_builder.japanese_corpus_occurrence import (
        JapaneseCorpusOccurrence,
    )

    occurrence = JapaneseCorpusOccurrence(
        part=JapaneseCorpusPart(
            kind=JapaneseCorpusPartKind.JAPANESE_LEXICAL,
            source_text="今日",
            processing_text="キョウ",
        ),
        source_start=0,
        source_end=2,
    )

    def fake_occurrence_tokenizer(
        text: str,
    ) -> tuple[JapaneseCorpusOccurrence, ...]:
        assert text == "今日"

        return (
            occurrence,
        )

    reader = JapaneseReader(
        tokenizer=lambda text: (text,),
        occurrence_tokenizer=fake_occurrence_tokenizer,
    )

    assert reader.read_occurrences(
        "今日"
    ) == (
        occurrence,
    )


def test_japanese_reader_read_occurrences_requires_occurrence_tokenizer() -> None:
    reader = JapaneseReader(
        tokenizer=lambda text: (text,)
    )

    with pytest.raises(
        RuntimeError,
        match="does not have an occurrence tokenizer",
    ):
        reader.read_occurrences(
            "日本語"
        )


def test_make_default_japanese_reader_supports_occurrences() -> None:
    reader = make_default_japanese_reader()

    occurrences = reader.read_occurrences(
        "〇"
    )

    assert len(occurrences) == 1

    occurrence = occurrences[0]

    assert (
        occurrence.part.kind
        is JapaneseCorpusPartKind.JAPANESE_LEXICAL
    )
    assert occurrence.part.source_text == "〇"
    assert occurrence.part.processing_text == "〇"
    assert occurrence.source_start == 0
    assert occurrence.source_end == 1

    occurrence.validate_source(
        "〇"
    )
