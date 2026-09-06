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


def test_normalize_text_removes_ignored_format_characters() -> None:
    from corpus_builder.text_normalizer import normalize_text

    assert normalize_text(
        "\ufeffABC\u200bテ\ufe0fスト\ufe0e"
    ) == "ABCテスト"


def test_normalize_text_removes_audited_format_characters() -> None:
    assert (
        normalize_text(
            "A"
            "\u202c"
            "B"
            "\u202a"
            "C"
            "\u200e"
            "D"
            "\u2060"
            "E"
        )
        == "ABCDE"
    )
def test_normalize_text_removes_observed_combining_noise_characters() -> None:
    assert normalize_text(
        "ア゚イ̆ウ̮̈エ"
    ) == "アイウエ"


def test_normalize_text_keeps_unrelated_combining_mark() -> None:
    assert normalize_text(
        "a\u0301"
    ) == "á"


def test_normalize_text_removes_observed_spacing_voiced_mark_noise() -> None:
    assert normalize_text(
        "CORNS゛での"
    ) == "CORNSでの"


def test_normalize_text_preserves_combining_voiced_kana() -> None:
    assert normalize_text(
        "カ\u3099"
    ) == "ガ"
