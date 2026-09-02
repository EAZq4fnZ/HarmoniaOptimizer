from corpus_builder.text_normalizer import (
    normalize_fullwidth_ascii,
    normalize_text,
    normalize_unicode,
    normalize_whitespace,
)


def test_normalize_whitespace_collapses_whitespace_runs() -> None:
    assert normalize_whitespace(
        "alpha\tbeta\n\ngamma   delta"
    ) == "alpha beta gamma delta"


def test_normalize_whitespace_strips_leading_and_trailing_whitespace() -> None:
    assert normalize_whitespace(
        "  alpha beta  "
    ) == "alpha beta"


def test_normalize_unicode_composes_canonical_equivalents() -> None:
    assert normalize_unicode(
        "e\u0301"
    ) == "é"


def test_normalize_unicode_preserves_compatibility_characters() -> None:
    assert normalize_unicode(
        "ＡＢＣ"
    ) == "ＡＢＣ"


def test_normalize_text_applies_unicode_then_whitespace_normalization() -> None:
    assert normalize_text(
        "  e\u0301\talpha\n "
    ) == "é alpha"


def test_normalize_fullwidth_ascii_converts_letters_and_digits() -> None:
    assert normalize_fullwidth_ascii(
        "ＡＢＣ１２３"
    ) == "ABC123"


def test_normalize_fullwidth_ascii_preserves_fullwidth_symbols() -> None:
    assert normalize_fullwidth_ascii(
        "Ａ！Ｂ？Ｃ"
    ) == "A！B？C"
