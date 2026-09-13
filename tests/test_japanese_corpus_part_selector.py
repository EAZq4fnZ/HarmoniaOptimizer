from dataclasses import dataclass

import pytest

from corpus_builder.japanese_corpus_part import (
    JapaneseCorpusPart,
    JapaneseCorpusPartKind,
)
from corpus_builder.sudachi_reader import (
    classify_sudachi_corpus_part,
    extract_sudachi_corpus_part_records,
    select_sudachi_corpus_part,
    select_sudachi_corpus_part_record,
)


@dataclass
class FakeMorpheme:
    surface_text: str
    reading_text: str
    pos: tuple[str, ...] = (
        "名詞",
        "普通名詞",
        "一般",
    )
    oov: bool = False

    def surface(self) -> str:
        return self.surface_text

    def reading_form(self) -> str:
        return self.reading_text

    def part_of_speech(self) -> tuple[str, ...]:
        return self.pos

    def is_oov(self) -> bool:
        return self.oov


def test_select_record_uses_reading_for_japanese_lexical_part() -> None:
    part = select_sudachi_corpus_part_record(
        FakeMorpheme(
            surface_text="今日",
            reading_text="キョウ",
        )
    )

    assert part is not None
    assert (
        part.kind
        is JapaneseCorpusPartKind.JAPANESE_LEXICAL
    )
    assert part.source_text == "今日"
    assert part.processing_text == "キョウ"


def test_select_record_preserves_ascii_literal() -> None:
    part = select_sudachi_corpus_part_record(
        FakeMorpheme(
            surface_text="Python",
            reading_text="パイソン",
        )
    )

    assert part is not None
    assert (
        part.kind
        is JapaneseCorpusPartKind.ASCII_LITERAL
    )
    assert part.source_text == "Python"
    assert part.processing_text == "Python"


@pytest.mark.parametrize(
    "surface",
    (
        "!",
        "?",
        "(",
        ")",
        "+",
        "++",
    ),
)
def test_select_record_classifies_ascii_punctuation(
    surface: str,
) -> None:
    part = select_sudachi_corpus_part_record(
        FakeMorpheme(
            surface_text=surface,
            reading_text=surface,
            pos=(
                "補助記号",
                "一般",
            ),
        )
    )

    assert part is not None
    assert (
        part.kind
        is JapaneseCorpusPartKind.PUNCTUATION
    )
    assert part.source_text == surface
    assert part.processing_text == surface


@pytest.mark.parametrize(
    "surface",
    (
        "、",
        "。",
        "－",
    ),
)
def test_select_record_classifies_harmonia_native_character(
    surface: str,
) -> None:
    part = select_sudachi_corpus_part_record(
        FakeMorpheme(
            surface_text=surface,
            reading_text=surface,
            pos=(
                "補助記号",
                "句点",
            ),
        )
    )

    assert part is not None
    assert (
        part.kind
        is JapaneseCorpusPartKind.HARMONIA_NATIVE
    )
    assert part.source_text == surface
    assert part.processing_text == surface


@pytest.mark.parametrize(
    "surface",
    (
        "！",
        "？",
        "（",
        "）",
        "｡",
        "､",
    ),
)
def test_select_record_classifies_resolved_punctuation(
    surface: str,
) -> None:
    part = select_sudachi_corpus_part_record(
        FakeMorpheme(
            surface_text=surface,
            reading_text=surface,
            pos=(
                "補助記号",
                "一般",
            ),
        )
    )

    assert part is not None
    assert (
        part.kind
        is JapaneseCorpusPartKind.PUNCTUATION
    )
    assert part.source_text == surface
    assert part.processing_text == surface


@pytest.mark.parametrize(
    "surface",
    (
        "〜",
        "〆",
        "α",
        "β",
        "μ",
        "Σ",
        "×",
        "○",
        "￥",
    ),
)
def test_select_record_classifies_unresolved_symbol_as_ambiguous(
    surface: str,
) -> None:
    part = select_sudachi_corpus_part_record(
        FakeMorpheme(
            surface_text=surface,
            reading_text=surface,
            pos=(
                "補助記号",
                "一般",
            ),
        )
    )

    assert part is not None
    assert (
        part.kind
        is JapaneseCorpusPartKind.AMBIGUOUS
    )
    assert part.source_text == surface
    assert part.processing_text == surface


def test_select_record_keeps_ideographic_zero_semantics() -> None:
    part = select_sudachi_corpus_part_record(
        FakeMorpheme(
            surface_text="〇",
            reading_text="〇",
        )
    )

    assert part is not None
    assert (
        part.kind
        is JapaneseCorpusPartKind.JAPANESE_LEXICAL
    )
    assert part.source_text == "〇"
    assert part.processing_text == "〇"


def test_select_record_preserves_plain_hiragana_oov_fallback() -> None:
    part = select_sudachi_corpus_part_record(
        FakeMorpheme(
            surface_text="ほげ",
            reading_text="ほげ",
            oov=True,
        )
    )

    assert part is not None
    assert (
        part.kind
        is JapaneseCorpusPartKind.JAPANESE_LEXICAL
    )
    assert part.source_text == "ほげ"
    assert part.processing_text == "ホゲ"


def test_select_record_returns_none_when_production_selector_skips_part() -> None:
    part = select_sudachi_corpus_part_record(
        FakeMorpheme(
            surface_text="   ",
            reading_text="   ",
        )
    )

    assert part is None


def test_unknown_non_ascii_symbol_is_conservatively_ambiguous() -> None:
    assert (
        classify_sudachi_corpus_part(
            surface="♡",
        )
        is JapaneseCorpusPartKind.AMBIGUOUS
    )


def test_empty_surface_remains_traceable() -> None:
    part = select_sudachi_corpus_part_record(
        FakeMorpheme(
            surface_text="",
            reading_text="．",
            pos=(
                "補助記号",
                "句点",
            ),
        )
    )

    assert part is not None
    assert part.source_text == ""
    assert part.processing_text == "．"
    assert (
        part.kind
        is JapaneseCorpusPartKind.JAPANESE_LEXICAL
    )

@pytest.mark.parametrize(
    (
        "surface",
        "reading",
        "pos",
        "oov",
        "expected",
    ),
    (
        (
            "今日",
            "キョウ",
            ("名詞", "普通名詞", "一般"),
            False,
            "キョウ",
        ),
        (
            "Python",
            "パイソン",
            ("名詞", "普通名詞", "一般"),
            False,
            "Python",
        ),
        (
            "〇",
            "〇",
            ("名詞", "普通名詞", "一般"),
            False,
            "〇",
        ),
        (
            "ほげ",
            "ほげ",
            ("名詞", "普通名詞", "一般"),
            True,
            "ホゲ",
        ),
        (
            "！",
            "！",
            ("補助記号", "一般"),
            False,
            "！",
        ),
    ),
)
def test_structured_record_preserves_legacy_processing_text(
    surface: str,
    reading: str,
    pos: tuple[str, ...],
    oov: bool,
    expected: str,
) -> None:
    morpheme = FakeMorpheme(
        surface_text=surface,
        reading_text=reading,
        pos=pos,
        oov=oov,
    )

    legacy = select_sudachi_corpus_part(
        morpheme
    )
    record = select_sudachi_corpus_part_record(
        morpheme
    )

    assert legacy == expected
    assert record is not None
    assert record.processing_text == legacy


def test_structured_record_can_retain_ambiguous_part_skipped_by_legacy() -> None:
    morpheme = FakeMorpheme(
        surface_text="〆",
        reading_text="〆",
        pos=(
            "補助記号",
            "一般",
        ),
    )

    assert (
        select_sudachi_corpus_part(
            morpheme
        )
        is None
    )

    record = select_sudachi_corpus_part_record(
        morpheme
    )

    assert record is not None
    assert (
        record.kind
        is JapaneseCorpusPartKind.AMBIGUOUS
    )
    assert record.source_text == "〆"
    assert record.processing_text == "〆"

def test_extract_sudachi_corpus_part_records_preserves_structured_parts() -> None:
    morphemes = (
        FakeMorpheme(
            surface_text="今日",
            reading_text="キョウ",
            pos=(
                "名詞",
                "普通名詞",
                "一般",
            ),
        ),
        FakeMorpheme(
            surface_text="Python",
            reading_text="パイソン",
            pos=(
                "名詞",
                "普通名詞",
                "一般",
            ),
        ),
        FakeMorpheme(
            surface_text="！",
            reading_text="！",
            pos=(
                "補助記号",
                "一般",
            ),
        ),
        FakeMorpheme(
            surface_text="〆",
            reading_text="〆",
            pos=(
                "補助記号",
                "一般",
            ),
        ),
        FakeMorpheme(
            surface_text=" ",
            reading_text=" ",
            pos=(
                "空白",
                "*",
            ),
        ),
    )

    parts = tuple(
        extract_sudachi_corpus_part_records(
            morphemes
        )
    )

    assert parts == (
        JapaneseCorpusPart(
            kind=JapaneseCorpusPartKind.JAPANESE_LEXICAL,
            source_text="今日",
            processing_text="キョウ",
        ),
        JapaneseCorpusPart(
            kind=JapaneseCorpusPartKind.ASCII_LITERAL,
            source_text="Python",
            processing_text="Python",
        ),
        JapaneseCorpusPart(
            kind=JapaneseCorpusPartKind.PUNCTUATION,
            source_text="！",
            processing_text="！",
        ),
        JapaneseCorpusPart(
            kind=JapaneseCorpusPartKind.AMBIGUOUS,
            source_text="〆",
            processing_text="〆",
        ),
    )


def test_extract_sudachi_corpus_part_records_returns_empty_for_only_whitespace() -> None:
    morphemes = (
        FakeMorpheme(
            surface_text=" ",
            reading_text=" ",
            pos=(
                "空白",
                "*",
            ),
        ),
        FakeMorpheme(
            surface_text="\t",
            reading_text="\t",
            pos=(
                "空白",
                "*",
            ),
        ),
    )

    assert tuple(
        extract_sudachi_corpus_part_records(
            morphemes
        )
    ) == ()
