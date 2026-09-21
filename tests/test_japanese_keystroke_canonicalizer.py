# test/test_japanese_keystroke_canonicalizer.py

import pytest

from corpus_builder.japanese_keystroke_canonicalizer import (
    DIRECT_JAPANESE_BRACKET_MAP,
    DIRECT_JAPANESE_PUNCTUATION_MAP,
    FULLWIDTH_ASCII_PUNCTUATION_MAP,
    HALFWIDTH_JAPANESE_PUNCTUATION_MAP,
    HARMONIA_NATIVE_CHARACTERS,
    canonicalize_japanese_keystroke_character,
    canonicalize_japanese_keystroke_text,
)


def test_harmonia_native_characters_are_preserved() -> None:
    assert HARMONIA_NATIVE_CHARACTERS == frozenset(
        {
            "、",
            "。",
            "－",
        }
    )

    assert canonicalize_japanese_keystroke_text(
        "、。－"
    ) == "、。－"


@pytest.mark.parametrize(
    ("source", "expected"),
    tuple(
        FULLWIDTH_ASCII_PUNCTUATION_MAP.items()
    ),
)
def test_fullwidth_ascii_punctuation_is_canonicalized(
    source: str,
    expected: str,
) -> None:
    assert canonicalize_japanese_keystroke_character(
        source
    ) == expected


def test_fullwidth_ascii_punctuation_sequence_is_canonicalized() -> None:
    assert canonicalize_japanese_keystroke_text(
        "！？：（）；［］＜＞"
    ) == "!?:();[]<>"


def test_fullwidth_hyphen_minus_does_not_override_harmonia_native_long_mark() -> None:
    assert "－" not in FULLWIDTH_ASCII_PUNCTUATION_MAP

    assert canonicalize_japanese_keystroke_character(
        "－"
    ) == "－"


@pytest.mark.parametrize(
    ("source", "expected"),
    tuple(
        HALFWIDTH_JAPANESE_PUNCTUATION_MAP.items()
    ),
)
def test_halfwidth_japanese_punctuation_is_canonicalized(
    source: str,
    expected: str,
) -> None:
    assert canonicalize_japanese_keystroke_character(
        source
    ) == expected


def test_halfwidth_japanese_punctuation_sequence_is_canonicalized() -> None:
    assert canonicalize_japanese_keystroke_text(
        "｢ﾃｽﾄ･ﾃﾞｽ｡｣"
    ) == "[ﾃｽﾄ/ﾃﾞｽ。]"


@pytest.mark.parametrize(
    ("source", "expected"),
    tuple(
        DIRECT_JAPANESE_BRACKET_MAP.items()
    ),
)
def test_direct_japanese_brackets_are_canonicalized(
    source: str,
    expected: str,
) -> None:
    assert canonicalize_japanese_keystroke_character(
        source
    ) == expected


def test_direct_japanese_bracket_sequence_is_canonicalized() -> None:
    assert canonicalize_japanese_keystroke_text(
        "「テスト」"
    ) == "[テスト]"


@pytest.mark.parametrize(
    ("source", "expected"),
    tuple(
        DIRECT_JAPANESE_PUNCTUATION_MAP.items()
    ),
)
def test_direct_japanese_punctuation_is_canonicalized(
    source: str,
    expected: str,
) -> None:
    assert canonicalize_japanese_keystroke_character(
        source
    ) == expected


def test_middle_dot_routes_are_canonicalized_to_slash() -> None:
    assert canonicalize_japanese_keystroke_character(
        "・"
    ) == "/"

    assert canonicalize_japanese_keystroke_character(
        "･"
    ) == "/"

    assert canonicalize_japanese_keystroke_text(
        "・･"
    ) == "//"


@pytest.mark.parametrize(
    "text",
    (
        "〜",
        "〆",
        "〆切",
        "α",
        "β",
        "μ",
        "㎡",
        "㎏",
        "①",
        "Ⅱ",
        "『",
        "』",
        "【",
        "】",
        "♡",
        "ω",
        "Σ",
    ),
)
def test_unresolved_characters_are_not_canonicalized(
    text: str,
) -> None:
    assert canonicalize_japanese_keystroke_text(
        text
    ) == text


def test_ascii_literal_is_preserved() -> None:
    assert canonicalize_japanese_keystroke_text(
        "ABC Python C++ https://example.com"
    ) == "ABC Python C++ https://example.com"


def test_mixed_resolved_and_unresolved_text() -> None:
    assert canonicalize_japanese_keystroke_text(
        "「ＡＢＣ！？」『〜〆㎡』、。－"
    ) == "[ＡＢＣ!?]『〜〆㎡』、。－"


def test_character_canonicalizer_rejects_empty_string() -> None:
    with pytest.raises(
        ValueError,
        match="char must contain exactly one character",
    ):
        canonicalize_japanese_keystroke_character(
            ""
        )


def test_character_canonicalizer_rejects_multiple_characters() -> None:
    with pytest.raises(
        ValueError,
        match="char must contain exactly one character",
    ):
        canonicalize_japanese_keystroke_character(
            "！？"
        )