import pytest

from corpus_builder.japanese_corpus_part import (
    JapaneseCorpusPartKind,
)
from corpus_builder.sudachi_reader import (
    extract_sudachi_corpus_parts,
    extract_sudachi_readings,
    make_default_sudachi_corpus_part_tokenizer,
    make_default_sudachi_tokenizer,
    make_sudachi_corpus_occurrence_tokenizer,
    make_sudachi_corpus_part_tokenizer,
    make_sudachi_tokenizer,
    select_sudachi_corpus_part,
    split_text_by_utf8_bytes,
)


class FakeMorpheme:
    def __init__(
        self,
        reading: str,
        surface: str | None = None,
        part_of_speech: str = "名詞",
    ) -> None:
        self._reading = reading
        self._surface = (
            reading
            if surface is None
            else surface
        )
        self._part_of_speech = part_of_speech

    def surface(
        self,
    ) -> str:
        return self._surface

    def reading_form(
        self,
    ) -> str:
        return self._reading

    def part_of_speech(
        self,
    ) -> tuple[str, ...]:
        return (
            self._part_of_speech,
            "*",
            "*",
            "*",
            "*",
            "*",
        )

    def is_oov(
        self,
    ) -> bool:
        return False


def test_extract_sudachi_readings_returns_reading_forms() -> None:
    morphemes = (
        FakeMorpheme("キョウ"),
        FakeMorpheme("ハ"),
        FakeMorpheme("テンキ"),
    )

    assert tuple(
        extract_sudachi_readings(morphemes)
    ) == (
        "キョウ",
        "ハ",
        "テンキ",
    )


def test_extract_sudachi_readings_rejects_empty_reading() -> None:
    morphemes = (
        FakeMorpheme("ニホン"),
        FakeMorpheme(""),
        FakeMorpheme("ゴ"),
    )

    with pytest.raises(
        ValueError,
        match="Sudachi reading must not be empty",
    ):
        tuple(
            extract_sudachi_readings(morphemes)
        )


def test_extract_sudachi_readings_rejects_non_string_reading() -> None:
    class InvalidMorpheme:
        def reading_form(
            self,
        ) -> str:
            return None  # type: ignore[return-value]

    with pytest.raises(
        TypeError,
        match="Sudachi reading must be a string",
    ):
        tuple(
            extract_sudachi_readings(
                (InvalidMorpheme(),)
            )
        )


def test_make_sudachi_tokenizer_reads_tokenize_result() -> None:
    class FakeTokenizer:
        def tokenize(
            self,
            text: str,
        ):
            assert text == "今日は天気です"
            return (
                FakeMorpheme("キョウ"),
                FakeMorpheme("ハ"),
                FakeMorpheme("テンキ"),
                FakeMorpheme("デス"),
            )

    tokenizer = make_sudachi_tokenizer(
        FakeTokenizer()
    )

    assert tuple(
        tokenizer("今日は天気です")
    ) == (
        "キョウ",
        "ハ",
        "テンキ",
        "デス",
    )


def test_make_default_sudachi_tokenizer_uses_core_dictionary() -> None:
    tokenizer = make_default_sudachi_tokenizer()

    assert tuple(
        tokenizer("今日は良い天気です")
    ) == (
        "キョウ",
        "ハ",
        "ヨイ",
        "テンキ",
        "デス",
    )


def test_extract_sudachi_corpus_parts_preserves_ascii_and_skips_whitespace() -> None:
    class SurfaceMorpheme:
        def __init__(
            self,
            surface: str,
            reading: str,
        ) -> None:
            self._surface = surface
            self._reading = reading

        def surface(
            self,
        ) -> str:
            return self._surface

        def reading_form(
            self,
        ) -> str:
            return self._reading

        def part_of_speech(
            self,
        ) -> tuple[str, ...]:
            return (
                "名詞",
                "*",
                "*",
                "*",
                "*",
                "*",
            )

        def is_oov(
            self,
        ) -> bool:
            return False

    morphemes = (
        SurfaceMorpheme(
            "ABC",
            "エービーシー",
        ),
        SurfaceMorpheme(
            " ",
            "キゴウ",
        ),
        SurfaceMorpheme(
            "今日",
            "キョウ",
        ),
        SurfaceMorpheme(
            "は",
            "ハ",
        ),
    )

    assert tuple(
        extract_sudachi_corpus_parts(morphemes)
    ) == (
        "ABC",
        "キョウ",
        "ハ",
    )


def test_make_sudachi_tokenizer_preserves_ascii_and_skips_whitespace() -> None:
    class SurfaceMorpheme:
        def __init__(
            self,
            surface: str,
            reading: str,
        ) -> None:
            self._surface = surface
            self._reading = reading

        def surface(
            self,
        ) -> str:
            return self._surface

        def reading_form(
            self,
        ) -> str:
            return self._reading

        def part_of_speech(
            self,
        ) -> tuple[str, ...]:
            return (
                "名詞",
                "*",
                "*",
                "*",
                "*",
                "*",
            )

        def is_oov(
            self,
        ) -> bool:
            return False

    class FakeTokenizer:
        def tokenize(
            self,
            text: str,
        ) -> tuple[SurfaceMorpheme, ...]:
            assert text == "ABC 日本語"

            return (
                SurfaceMorpheme(
                    "ABC",
                    "エービーシー",
                ),
                SurfaceMorpheme(
                    " ",
                    "キゴウ",
                ),
                SurfaceMorpheme(
                    "日本語",
                    "ニホンゴ",
                ),
            )

    tokenizer = make_sudachi_tokenizer(
        FakeTokenizer()
    )

    assert tuple(
        tokenizer("ABC 日本語")
    ) == (
        "ABC",
        "ニホンゴ",
    )


def test_extract_sudachi_corpus_parts_preserves_symbols() -> None:
    tokenizer = make_default_sudachi_tokenizer()

    assert "".join(
        tokenizer("今日は良い天気です。")
    ) == "キョウハヨイテンキデス。"

    assert "".join(
        tokenizer("「テスト！」")
    ) == "「テスト！」"

    assert "".join(
        tokenizer("：（）；")
    ) == "：（）；"


def test_extract_sudachi_corpus_parts_uses_surface_for_symbols() -> None:
    morphemes = (
        FakeMorpheme(
            reading="キゴウ",
            surface="：",
            part_of_speech="補助記号",
        ),
        FakeMorpheme(
            reading="!",
            surface="！",
            part_of_speech="補助記号",
        ),
        FakeMorpheme(
            reading="キゴウ",
            surface="（",
            part_of_speech="補助記号",
        ),
    )

    assert tuple(
        extract_sudachi_corpus_parts(morphemes)
    ) == (
        "：",
        "！",
        "（",
    )


def test_select_sudachi_corpus_part_returns_none_for_whitespace() -> None:
    from corpus_builder.sudachi_reader import (
        select_sudachi_corpus_part,
    )

    morpheme = FakeMorpheme(
        reading="キゴウ",
        surface=" ",
    )

    assert select_sudachi_corpus_part(
        morpheme
    ) is None


def test_select_sudachi_corpus_part_uses_surface_for_symbol() -> None:
    from corpus_builder.sudachi_reader import (
        select_sudachi_corpus_part,
    )

    morpheme = FakeMorpheme(
        reading="キゴウ",
        surface="：",
        part_of_speech="補助記号",
    )

    assert select_sudachi_corpus_part(
        morpheme
    ) == "："


def test_select_sudachi_corpus_part_uses_surface_for_ascii() -> None:
    from corpus_builder.sudachi_reader import (
        select_sudachi_corpus_part,
    )

    morpheme = FakeMorpheme(
        reading="エービーシー",
        surface="ABC",
    )

    assert select_sudachi_corpus_part(
        morpheme
    ) == "ABC"


def test_select_sudachi_corpus_part_uses_reading_for_japanese() -> None:
    from corpus_builder.sudachi_reader import (
        select_sudachi_corpus_part,
    )

    morpheme = FakeMorpheme(
        reading="キョウ",
        surface="今日",
    )

    assert select_sudachi_corpus_part(
        morpheme
    ) == "キョウ"


def test_select_sudachi_corpus_part_uses_reading_for_empty_symbol_surface() -> None:
    from corpus_builder.sudachi_reader import (
        select_sudachi_corpus_part,
    )

    morpheme = FakeMorpheme(
        reading="．",
        surface="",
        part_of_speech="補助記号",
    )

    assert select_sudachi_corpus_part(
        morpheme
    ) == "．"


def test_select_sudachi_corpus_part_converts_plain_hiragana_oov_to_katakana() -> None:
    from corpus_builder.sudachi_reader import (
        select_sudachi_corpus_part,
    )

    class OovMorpheme:
        def surface(
            self,
        ) -> str:
            return "す"

        def reading_form(
            self,
        ) -> str:
            return "す"

        def part_of_speech(
            self,
        ) -> tuple[str, ...]:
            return (
                "名詞",
                "普通名詞",
                "一般",
                "*",
                "*",
                "*",
            )

        def is_oov(
            self,
        ) -> bool:
            return True

    assert select_sudachi_corpus_part(
        OovMorpheme()
    ) == "ス"


def test_select_sudachi_corpus_part_does_not_fallback_for_known_hiragana() -> None:
    from corpus_builder.sudachi_reader import (
        select_sudachi_corpus_part,
    )

    class KnownMorpheme:
        def surface(
            self,
        ) -> str:
            return "す"

        def reading_form(
            self,
        ) -> str:
            return "ス"

        def part_of_speech(
            self,
        ) -> tuple[str, ...]:
            return (
                "助動詞",
                "*",
                "*",
                "*",
                "*",
                "*",
            )

        def is_oov(
            self,
        ) -> bool:
            return False

    assert select_sudachi_corpus_part(
        KnownMorpheme()
    ) == "ス"


def test_select_sudachi_corpus_part_skips_unreadable_cjk_oov() -> None:
    from corpus_builder.sudachi_reader import (
        select_sudachi_corpus_part,
    )

    class OovMorpheme:
        def surface(
            self,
        ) -> str:
            return "激"

        def reading_form(
            self,
        ) -> str:
            return "激"

        def part_of_speech(
            self,
        ) -> tuple[str, ...]:
            return (
                "名詞",
                "普通名詞",
                "一般",
                "*",
                "*",
                "*",
            )

        def is_oov(
            self,
        ) -> bool:
            return True

    assert select_sudachi_corpus_part(
        OovMorpheme()
    ) is None


def test_select_sudachi_corpus_part_skips_unreadable_cjk_oov_reading() -> None:
    from corpus_builder.sudachi_reader import (
        select_sudachi_corpus_part,
    )

    class OovMorpheme:
        def surface(
            self,
        ) -> str:
            return "蜃（しん）"

        def reading_form(
            self,
        ) -> str:
            return "蜃"

        def part_of_speech(
            self,
        ) -> tuple[str, ...]:
            return (
                "名詞",
                "普通名詞",
                "一般",
                "*",
                "*",
                "*",
            )

        def is_oov(
            self,
        ) -> bool:
            return True

    assert select_sudachi_corpus_part(
        OovMorpheme()
    ) is None


def test_select_sudachi_corpus_part_skips_unreadable_cjk_oov_with_iteration_mark() -> None:
    from corpus_builder.sudachi_reader import (
        select_sudachi_corpus_part,
    )

    class OovMorpheme:
        def surface(
            self,
        ) -> str:
            return "夫々"

        def reading_form(
            self,
        ) -> str:
            return "夫々"

        def part_of_speech(
            self,
        ) -> tuple[str, ...]:
            return (
                "名詞",
                "普通名詞",
                "一般",
                "*",
                "*",
                "*",
            )

        def is_oov(
            self,
        ) -> bool:
            return True

    assert select_sudachi_corpus_part(
        OovMorpheme()
    ) is None


def test_select_sudachi_corpus_part_preserves_unreadable_cyrillic_oov() -> None:
    from corpus_builder.sudachi_reader import (
        select_sudachi_corpus_part,
    )

    class OovMorpheme:
        def surface(
            self,
        ) -> str:
            return "галина"

        def reading_form(
            self,
        ) -> str:
            return "галина"

        def part_of_speech(
            self,
        ) -> tuple[str, ...]:
            return (
                "名詞",
                "普通名詞",
                "一般",
                "*",
                "*",
                "*",
            )

        def is_oov(
            self,
        ) -> bool:
            return True

    assert select_sudachi_corpus_part(
        OovMorpheme()
    ) == "галина"


def test_select_sudachi_corpus_part_does_not_fallback_for_small_hiragana_oov() -> None:
    from corpus_builder.sudachi_reader import (
        select_sudachi_corpus_part,
    )

    class OovMorpheme:
        def surface(
            self,
        ) -> str:
            return "ぇ"

        def reading_form(
            self,
        ) -> str:
            return "ぇ"

        def part_of_speech(
            self,
        ) -> tuple[str, ...]:
            return (
                "名詞",
                "普通名詞",
                "一般",
                "*",
                "*",
                "*",
            )

        def is_oov(
            self,
        ) -> bool:
            return True

    assert select_sudachi_corpus_part(
        OovMorpheme()
    ) == "ぇ"


def test_select_sudachi_corpus_part_does_not_fallback_for_small_tsu_oov() -> None:
    from corpus_builder.sudachi_reader import (
        select_sudachi_corpus_part,
    )

    class OovMorpheme:
        def surface(
            self,
        ) -> str:
            return "っ"

        def reading_form(
            self,
        ) -> str:
            return "っ"

        def part_of_speech(
            self,
        ) -> tuple[str, ...]:
            return (
                "名詞",
                "普通名詞",
                "一般",
                "*",
                "*",
                "*",
            )

        def is_oov(
            self,
        ) -> bool:
            return True

    assert select_sudachi_corpus_part(
        OovMorpheme()
    ) == "っ"


def test_select_sudachi_corpus_part_prefers_sudachi_reading_when_oov_reading_differs_from_surface() -> None:
    from corpus_builder.sudachi_reader import (
        select_sudachi_corpus_part,
    )

    class OovMorpheme:
        def surface(
            self,
        ) -> str:
            return "す"

        def reading_form(
            self,
        ) -> str:
            return "ス"

        def part_of_speech(
            self,
        ) -> tuple[str, ...]:
            return (
                "名詞",
                "普通名詞",
                "一般",
                "*",
                "*",
                "*",
            )

        def is_oov(
            self,
        ) -> bool:
            return True

    assert select_sudachi_corpus_part(
        OovMorpheme()
    ) == "ス"


def test_select_sudachi_corpus_part_skips_auxiliary_symbol_containing_letter() -> None:
    from corpus_builder.sudachi_reader import (
        select_sudachi_corpus_part,
    )

    morpheme = FakeMorpheme(
        reading="(株)",
        surface="(株)",
        part_of_speech="補助記号",
    )

    assert (
        select_sudachi_corpus_part(
            morpheme
        )
        is None
    )


def test_select_sudachi_corpus_part_skips_auxiliary_symbol_iteration_mark() -> None:
    from corpus_builder.sudachi_reader import (
        select_sudachi_corpus_part,
    )

    morpheme = FakeMorpheme(
        reading="々",
        surface="々",
        part_of_speech="補助記号",
    )

    assert (
        select_sudachi_corpus_part(
            morpheme
        )
        is None
    )


def test_select_sudachi_corpus_part_preserves_punctuation_and_symbols() -> None:
    from corpus_builder.sudachi_reader import (
        select_sudachi_corpus_part,
    )

    for surface in (
        "：",
        "！",
        "（",
        "☆",
        "「」",
        "！？",
    ):
        morpheme = FakeMorpheme(
            reading="キゴウ",
            surface=surface,
            part_of_speech="補助記号",
        )

        assert (
            select_sudachi_corpus_part(
                morpheme
            )
            == surface
        )


def test_select_sudachi_corpus_part_preserves_supported_japanese_auxiliary_text() -> None:
    for surface in (
        "ー",
        "ーー",
        "ァ",
        "ッ",
        "ぁ",
        "っ",
    ):
        morpheme = FakeMorpheme(
            reading=surface,
            surface=surface,
            part_of_speech="補助記号",
        )

        assert (
            select_sudachi_corpus_part(
                morpheme
            )
            == surface
        )


def test_make_sudachi_tokenizer_chunks_large_input_before_raw_tokenizer() -> None:
    received: list[str] = []

    class ByteLimitedTokenizer:
        def tokenize(
            self,
            text: str,
        ) -> tuple[FakeMorpheme, ...]:
            received.append(text)

            if len(text.encode("utf-8")) > 48_000:
                raise ValueError(
                    "Sudachi input exceeds byte limit"
                )

            return (
                FakeMorpheme(
                    reading="ア",
                    surface="あ",
                ),
            )

    reader = make_sudachi_tokenizer(
        ByteLimitedTokenizer()
    )

    result = tuple(
        reader(
            "あ" * 20_000
        )
    )

    assert len(received) > 1

    assert all(
        len(chunk.encode("utf-8"))
        <= 48_000
        for chunk in received
    )

    assert result == tuple(
        "ア"
        for _ in received
    )


def test_split_text_by_utf8_bytes_returns_empty_for_empty_text() -> None:
    assert split_text_by_utf8_bytes(
        ""
    ) == ()


def test_split_text_by_utf8_bytes_keeps_text_at_exact_byte_limit() -> None:
    text = "あ" * 16_000

    assert len(
        text.encode("utf-8")
    ) == 48_000

    assert split_text_by_utf8_bytes(
        text
    ) == (
        text,
    )


def test_split_text_by_utf8_bytes_preserves_text_across_chunks() -> None:
    text = (
        "ABC"
        + "あ" * 20_000
        + "XYZ"
    )

    chunks = split_text_by_utf8_bytes(
        text
    )

    assert len(chunks) > 1

    assert all(
        len(chunk.encode("utf-8"))
        <= 48_000
        for chunk in chunks
    )

    assert "".join(
        chunks
    ) == text


def test_split_text_by_utf8_bytes_rejects_non_positive_limit() -> None:
    with pytest.raises(
        ValueError,
        match="max_bytes must be greater than 0",
    ):
        split_text_by_utf8_bytes(
            "テスト",
            max_bytes=0,
        )


def test_split_text_by_utf8_bytes_prefers_nearby_natural_boundary() -> None:
    text = (
        "あ" * 15_990
        + "。"
        + "い" * 1_000
    )

    chunks = split_text_by_utf8_bytes(
        text
    )

    assert len(chunks) == 2

    assert chunks[0].endswith(
        "。"
    )

    assert "".join(
        chunks
    ) == text

    assert all(
        len(chunk.encode("utf-8"))
        <= 48_000
        for chunk in chunks
    )


def test_split_text_by_utf8_bytes_falls_back_to_hard_cut_without_boundary() -> None:
    text = (
        "あ" * 20_000
    )

    chunks = split_text_by_utf8_bytes(
        text
    )

    assert len(chunks) == 2

    assert "".join(
        chunks
    ) == text

    assert all(
        len(chunk.encode("utf-8"))
        <= 48_000
        for chunk in chunks
    )


def test_split_text_by_utf8_bytes_ignores_natural_boundary_beyond_lookback() -> None:
    text = (
        "。"
        + "a" * 1_200
    )

    chunks = split_text_by_utf8_bytes(
        text,
        max_bytes=1_000,
    )

    assert len(chunks) == 2

    assert chunks[0].startswith(
        "。"
    )

    assert not chunks[0].endswith(
        "。"
    )

    assert len(
        chunks[0].encode("utf-8")
    ) == 1_000

    assert "".join(
        chunks
    ) == text

def test_select_sudachi_corpus_part_uses_reading_for_empty_non_symbol_surface() -> None:
    morpheme = FakeMorpheme(
        reading="ニ",
        surface="",
        part_of_speech="名詞",
    )

    assert select_sudachi_corpus_part(
        morpheme
    ) == "ニ"


def test_select_sudachi_corpus_part_rejects_empty_surface_with_empty_reading() -> None:
    morpheme = FakeMorpheme(
        reading="",
        surface="",
        part_of_speech="名詞",
    )

    with pytest.raises(
        ValueError,
        match="Sudachi reading must not be empty",
    ):
        select_sudachi_corpus_part(
            morpheme
        )



def test_make_sudachi_tokenizer_salvages_cjk_oov_after_ideographic_zero() -> None:
    class OovMorpheme(FakeMorpheme):
        def is_oov(
            self,
        ) -> bool:
            return True

    received: list[str] = []

    class FakeTokenizer:
        def tokenize(
            self,
            text: str,
        ):
            received.append(text)

            if text == "〇魚菜店":
                return (
                    OovMorpheme(
                        reading="〇魚菜店",
                        surface="〇魚菜店",
                    ),
                )

            if text == "魚菜店":
                return (
                    FakeMorpheme(
                        reading="サカナ",
                        surface="魚",
                    ),
                    FakeMorpheme(
                        reading="ナ",
                        surface="菜",
                    ),
                    FakeMorpheme(
                        reading="テン",
                        surface="店",
                    ),
                )

            raise AssertionError(
                f"Unexpected tokenize input: {text!r}"
            )

    reader = make_sudachi_tokenizer(
        FakeTokenizer()
    )

    assert tuple(
        reader("〇魚菜店")
    ) == (
        "〇",
        "サカナ",
        "ナ",
        "テン",
    )

    assert received == [
        "〇魚菜店",
        "魚菜店",
    ]


def test_make_sudachi_tokenizer_does_not_salvage_plain_cjk_oov() -> None:
    class OovMorpheme(FakeMorpheme):
        def is_oov(
            self,
        ) -> bool:
            return True

    received: list[str] = []

    class FakeTokenizer:
        def tokenize(
            self,
            text: str,
        ):
            received.append(text)

            if text == "蜃":
                return (
                    OovMorpheme(
                        reading="蜃",
                        surface="蜃",
                    ),
                )

            raise AssertionError(
                f"Unexpected tokenize input: {text!r}"
            )

    reader = make_sudachi_tokenizer(
        FakeTokenizer()
    )

    assert tuple(
        reader("蜃")
    ) == ()

    assert received == [
        "蜃",
    ]



def test_make_sudachi_tokenizer_salvages_ideographic_zero_before_known_phrase() -> None:
    class OovMorpheme(FakeMorpheme):
        def is_oov(
            self,
        ) -> bool:
            return True

    class FakeTokenizer:
        def tokenize(
            self,
            text: str,
        ):
            if text == "〇東温市民花火":
                return (
                    OovMorpheme(
                        reading="〇東温市民花火",
                        surface="〇東温市民花火",
                    ),
                )

            if text == "東温市民花火":
                return (
                    FakeMorpheme(
                        reading="トウオン",
                        surface="東温",
                    ),
                    FakeMorpheme(
                        reading="シミン",
                        surface="市民",
                    ),
                    FakeMorpheme(
                        reading="ハナビ",
                        surface="花火",
                    ),
                )

            raise AssertionError(
                f"Unexpected tokenize input: {text!r}"
            )

    reader = make_sudachi_tokenizer(
        FakeTokenizer()
    )

    assert tuple(
        reader("〇東温市民花火")
    ) == (
        "〇",
        "トウオン",
        "シミン",
        "ハナビ",
    )



def test_select_sudachi_corpus_part_skips_repeated_iteration_mark_emoticon_oov() -> None:
    class OovMorpheme(FakeMorpheme):
        def is_oov(
            self,
        ) -> bool:
            return True

    morpheme = OovMorpheme(
        reading="ノヽノヽノヽノ",
        surface="ﾉヽﾉヽﾉヽﾉ",
    )

    assert select_sudachi_corpus_part(
        morpheme
    ) is None


def test_select_sudachi_corpus_part_does_not_skip_short_iteration_mark_oov() -> None:
    class OovMorpheme(FakeMorpheme):
        def is_oov(
            self,
        ) -> bool:
            return True

    morpheme = OovMorpheme(
        reading="ノヽノ",
        surface="ﾉヽﾉ",
    )

    assert select_sudachi_corpus_part(
        morpheme
    ) == "ノヽノ"


def test_make_default_sudachi_tokenizer_preserves_standalone_ideographic_zero() -> None:
    reader = make_default_sudachi_tokenizer()

    assert "".join(
        reader("〇")
    ) == "〇"

def test_make_sudachi_corpus_part_tokenizer_returns_structured_parts() -> None:
    class FakeTokenizer:
        def tokenize(
            self,
            text: str,
        ):
            assert text == "今日Python！"

            return (
                FakeMorpheme(
                    "キョウ",
                    surface="今日",
                ),
                FakeMorpheme(
                    "パイソン",
                    surface="Python",
                ),
                FakeMorpheme(
                    "！",
                    surface="！",
                    part_of_speech="補助記号",
                ),
            )

    read = make_sudachi_corpus_part_tokenizer(
        FakeTokenizer()
    )

    parts = tuple(
        read("今日Python！")
    )

    assert tuple(
        (
            part.kind,
            part.source_text,
            part.processing_text,
        )
        for part in parts
    ) == (
        (
            JapaneseCorpusPartKind.JAPANESE_LEXICAL,
            "今日",
            "キョウ",
        ),
        (
            JapaneseCorpusPartKind.ASCII_LITERAL,
            "Python",
            "Python",
        ),
        (
            JapaneseCorpusPartKind.PUNCTUATION,
            "！",
            "！",
        ),
    )

def test_make_sudachi_corpus_part_tokenizer_preserves_ideographic_zero_in_cjk_oov() -> None:
    class FakeOovMorpheme(FakeMorpheme):
        def is_oov(
            self,
        ) -> bool:
            return True

    class FakeTokenizer:
        def tokenize(
            self,
            text: str,
        ):
            if text == "〇魚":
                return (
                    FakeOovMorpheme(
                        "〇魚",
                        surface="〇魚",
                    ),
                )

            if text == "魚":
                return (
                    FakeMorpheme(
                        "サカナ",
                        surface="魚",
                    ),
                )

            raise AssertionError(
                f"Unexpected text: {text!r}"
            )

    read = make_sudachi_corpus_part_tokenizer(
        FakeTokenizer()
    )

    parts = tuple(
        read("〇魚")
    )

    assert tuple(
        (
            part.kind,
            part.source_text,
            part.processing_text,
        )
        for part in parts
    ) == (
        (
            JapaneseCorpusPartKind.JAPANESE_LEXICAL,
            "〇",
            "〇",
        ),
        (
            JapaneseCorpusPartKind.JAPANESE_LEXICAL,
            "魚",
            "サカナ",
        ),
    )

def test_make_default_sudachi_corpus_part_tokenizer_preserves_standalone_ideographic_zero() -> None:
    reader = make_default_sudachi_corpus_part_tokenizer()

    parts = tuple(
        reader("〇")
    )

    assert len(parts) == 1

    part = parts[0]

    assert (
        part.kind
        is JapaneseCorpusPartKind.JAPANESE_LEXICAL
    )
    assert part.source_text == "〇"
    assert part.processing_text == "〇"

class PositionalFakeMorpheme(FakeMorpheme):
    def __init__(
        self,
        reading: str,
        *,
        surface: str | None = None,
        part_of_speech: str = "名詞",
        begin: int,
        end: int,
        is_oov: bool = False,
    ) -> None:
        super().__init__(
            reading,
            surface=surface,
            part_of_speech=part_of_speech,
        )
        self._begin = begin
        self._end = end
        self._is_oov = is_oov

    def begin(
        self,
    ) -> int:
        return self._begin

    def end(
        self,
    ) -> int:
        return self._end

    def is_oov(
        self,
    ) -> bool:
        return self._is_oov


def test_occurrence_tokenizer_preserves_exact_source_spans(
) -> None:
    class FakeTokenizer:
        def tokenize(
            self,
            text: str,
        ):
            assert text == "今日Python！"

            return (
                PositionalFakeMorpheme(
                    "キョウ",
                    surface="今日",
                    begin=0,
                    end=2,
                ),
                PositionalFakeMorpheme(
                    "パイソン",
                    surface="Python",
                    begin=2,
                    end=8,
                ),
                PositionalFakeMorpheme(
                    "！",
                    surface="！",
                    part_of_speech="補助記号",
                    begin=8,
                    end=9,
                ),
            )

    read = make_sudachi_corpus_occurrence_tokenizer(
        FakeTokenizer()
    )

    source = "今日Python！"

    occurrences = tuple(
        read(source)
    )

    assert tuple(
        (
            occurrence.part.source_text,
            occurrence.part.processing_text,
            occurrence.source_start,
            occurrence.source_end,
        )
        for occurrence in occurrences
    ) == (
        (
            "今日",
            "キョウ",
            0,
            2,
        ),
        (
            "Python",
            "Python",
            2,
            8,
        ),
        (
            "！",
            "！",
            8,
            9,
        ),
    )

    for occurrence in occurrences:
        occurrence.validate_source(
            source
        )


def test_occurrence_tokenizer_tracks_chunk_absolute_offsets(
) -> None:
    received: list[str] = []

    class FakeTokenizer:
        def tokenize(
            self,
            text: str,
        ):
            received.append(text)

            return (
                PositionalFakeMorpheme(
                    "ア",
                    surface=text[0],
                    begin=0,
                    end=1,
                ),
            )

    read = make_sudachi_corpus_occurrence_tokenizer(
        FakeTokenizer()
    )

    source = "あ" * 20_000

    occurrences = tuple(
        read(source)
    )

    assert len(received) > 1
    assert len(occurrences) == len(received)

    expected_start = 0

    for occurrence, chunk in zip(
        occurrences,
        received,
        strict=True,
    ):
        assert occurrence.source_start == expected_start
        assert occurrence.source_end == expected_start + 1

        occurrence.validate_source(
            source
        )

        expected_start += len(
            chunk
        )


def test_occurrence_tokenizer_tracks_ideographic_zero_salvage_spans(
) -> None:
    class FakeTokenizer:
        def tokenize(
            self,
            text: str,
        ):
            if text == "〇魚菜店":
                return (
                    PositionalFakeMorpheme(
                        "〇魚菜店",
                        surface="〇魚菜店",
                        begin=0,
                        end=4,
                        is_oov=True,
                    ),
                )

            if text == "魚菜店":
                return (
                    PositionalFakeMorpheme(
                        "サカナ",
                        surface="魚",
                        begin=0,
                        end=1,
                    ),
                    PositionalFakeMorpheme(
                        "ナ",
                        surface="菜",
                        begin=1,
                        end=2,
                    ),
                    PositionalFakeMorpheme(
                        "テン",
                        surface="店",
                        begin=2,
                        end=3,
                    ),
                )

            raise AssertionError(
                f"Unexpected tokenize input: {text!r}"
            )

    read = make_sudachi_corpus_occurrence_tokenizer(
        FakeTokenizer()
    )

    source = "〇魚菜店"

    occurrences = tuple(
        read(source)
    )

    assert tuple(
        (
            occurrence.part.source_text,
            occurrence.source_start,
            occurrence.source_end,
        )
        for occurrence in occurrences
    ) == (
        (
            "〇",
            0,
            1,
        ),
        (
            "魚",
            1,
            2,
        ),
        (
            "菜",
            2,
            3,
        ),
        (
            "店",
            3,
            4,
        ),
    )

    for occurrence in occurrences:
        occurrence.validate_source(
            source
        )


def test_occurrence_tokenizer_tracks_middle_ideographic_zero_spans(
) -> None:
    class FakeTokenizer:
        def tokenize(
            self,
            text: str,
        ):
            if text == "魚〇店":
                return (
                    PositionalFakeMorpheme(
                        "魚〇店",
                        surface="魚〇店",
                        begin=0,
                        end=3,
                        is_oov=True,
                    ),
                )

            if text == "魚":
                return (
                    PositionalFakeMorpheme(
                        "サカナ",
                        surface="魚",
                        begin=0,
                        end=1,
                    ),
                )

            if text == "店":
                return (
                    PositionalFakeMorpheme(
                        "テン",
                        surface="店",
                        begin=0,
                        end=1,
                    ),
                )

            raise AssertionError(
                f"Unexpected tokenize input: {text!r}"
            )

    read = make_sudachi_corpus_occurrence_tokenizer(
        FakeTokenizer()
    )

    source = "魚〇店"

    occurrences = tuple(
        read(source)
    )

    assert tuple(
        (
            occurrence.part.source_text,
            occurrence.source_start,
            occurrence.source_end,
        )
        for occurrence in occurrences
    ) == (
        (
            "魚",
            0,
            1,
        ),
        (
            "〇",
            1,
            2,
        ),
        (
            "店",
            2,
            3,
        ),
    )


def test_occurrence_tokenizer_requires_positional_morphemes(
) -> None:
    class FakeTokenizer:
        def tokenize(
            self,
            text: str,
        ):
            return (
                FakeMorpheme(
                    "キョウ",
                    surface="今日",
                ),
            )

    read = make_sudachi_corpus_occurrence_tokenizer(
        FakeTokenizer()
    )

    with pytest.raises(
        TypeError,
        match="must provide begin",
    ):
        tuple(
            read("今日")
        )

@pytest.mark.parametrize(
    "surface",
    (
        "「",
        "」",
        "｢",
        "｣",
    ),
)
def test_classify_sudachi_corpus_part_resolves_direct_japanese_brackets_as_punctuation(
    surface: str,
) -> None:
    from corpus_builder.sudachi_reader import (
        classify_sudachi_corpus_part,
    )

    assert (
        classify_sudachi_corpus_part(
            surface=surface
        )
        is JapaneseCorpusPartKind.PUNCTUATION
    )


@pytest.mark.parametrize(
    "surface",
    (
        "『",
        "』",
        "【",
        "】",
    ),
)
def test_classify_sudachi_corpus_part_keeps_conversion_brackets_ambiguous(
    surface: str,
) -> None:
    from corpus_builder.sudachi_reader import (
        classify_sudachi_corpus_part,
    )

    assert (
        classify_sudachi_corpus_part(
            surface=surface
        )
        is JapaneseCorpusPartKind.AMBIGUOUS
    )