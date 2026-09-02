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
