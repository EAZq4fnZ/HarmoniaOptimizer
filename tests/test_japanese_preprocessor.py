import pytest

from corpus_builder.japanese_preprocessor import (
    preprocess_japanese_source,
)
from corpus_builder.japanese_reader import make_default_japanese_reader


def test_preprocess_japanese_source_applies_common_normalization() -> None:
    assert preprocess_japanese_source(
        "  ＡＢＣ\tテスト\n "
    ) == "ABC テスト"


def test_preprocess_japanese_source_applies_reader_after_normalization() -> None:
    received: list[str] = []

    def fake_reader(text: str) -> str:
        received.append(text)
        return "テストヨミ"

    result = preprocess_japanese_source(
        "  ＡＢＣ\tテスト\n ",
        reader=fake_reader,
    )

    assert received == [
        "ABC テスト"
    ]
    assert result == "テストヨミ"


def test_preprocess_japanese_source_normalizes_reader_output() -> None:
    def fake_reader(text: str) -> str:
        return "  テスト\tヨミ\n "

    assert preprocess_japanese_source(
        "テスト",
        reader=fake_reader,
    ) == "テスト ヨミ"


def test_preprocess_japanese_source_rejects_empty_reader_output() -> None:
    def fake_reader(text: str) -> str:
        return "   \t\n"

    with pytest.raises(
        ValueError,
        match="reader output must not be empty",
    ):
        preprocess_japanese_source(
            "テスト",
            reader=fake_reader,
        )


def test_preprocess_japanese_source_rejects_non_string_reader_output() -> None:
    def fake_reader(text: str) -> str:
        return None  # type: ignore[return-value]

    with pytest.raises(
        TypeError,
        match="reader output must be a string",
    ):
        preprocess_japanese_source(
            "テスト",
            reader=fake_reader,
        )


def test_preprocess_japanese_source_with_default_reader() -> None:
    assert preprocess_japanese_source(
        "  ＡＢＣ\t今日は良い天気です\n ",
        reader=make_default_japanese_reader(),
    ) == "ABCキョウハヨイテンキデス"
