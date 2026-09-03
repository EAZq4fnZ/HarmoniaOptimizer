import pytest

from corpus_builder.sudachi_reader import (
    extract_sudachi_corpus_parts,
    extract_sudachi_readings,
    make_default_sudachi_tokenizer,
    make_sudachi_tokenizer,
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
