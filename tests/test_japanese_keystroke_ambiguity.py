from corpus_builder.japanese_keystroke_ambiguity import (
    JapaneseKeystrokeAmbiguityClass,
    classify_japanese_keystroke_ambiguity,
)


def assert_class(
    expected: JapaneseKeystrokeAmbiguityClass,
    *source_texts: str,
) -> None:
    for source_text in source_texts:
        assert (
            classify_japanese_keystroke_ambiguity(
                source_text
            )
            is expected
        )


def test_classifies_japanese_punctuation() -> None:
    assert_class(
        JapaneseKeystrokeAmbiguityClass
        .JAPANESE_PUNCTUATION,
        "「",
        "」",
        "『",
        "』",
        "【",
        "】",
        "・",
        "…",
    )


def test_classifies_wave_dash_input_method() -> None:
    assert_class(
        JapaneseKeystrokeAmbiguityClass
        .INPUT_METHOD,
        "〜",
        "な〜",
        "ね〜",
        "よ〜",
        "です〜",
        "で〜",
        "も〜",
    )


def test_classifies_semantic_symbols() -> None:
    assert_class(
        JapaneseKeystrokeAmbiguityClass
        .SEMANTIC_SYMBOL,
        "α",
        "β",
        "μ",
        "Σ",
        "×",
        "○",
        "￥",
        "〆",
    )


def test_classifies_technical_compatibility() -> None:
    assert_class(
        JapaneseKeystrokeAmbiguityClass
        .COMPATIBILITY,
        "℃",
        "㎡",
        "㎏",
        "㎞",
        "㎝",
        "²",
        "³",
    )


def test_classifies_circled_digits_as_compatibility() -> None:
    assert_class(
        JapaneseKeystrokeAmbiguityClass
        .COMPATIBILITY,
        "①",
        "②",
        "⑩",
        "⑳",
    )


def test_classifies_roman_numerals_as_compatibility() -> None:
    assert_class(
        JapaneseKeystrokeAmbiguityClass
        .COMPATIBILITY,
        "Ⅰ",
        "Ⅱ",
        "Ⅸ",
        "ⅰ",
        "ⅷ",
    )


def test_classifies_typographic_characters() -> None:
    assert_class(
        JapaneseKeystrokeAmbiguityClass
        .TYPOGRAPHIC,
        "“",
        "”",
        "‘",
        "’",
        "«",
        "»",
        "―",
        "—",
        "–",
        "‐",
        "−",
        "´",
    )


def test_classifies_directional_symbols() -> None:
    assert_class(
        JapaneseKeystrokeAmbiguityClass
        .DIRECTIONAL_SYMBOL,
        "→",
        "←",
        "↑",
        "↓",
        "⇒",
        "▶",
    )


def test_classifies_geometric_symbols() -> None:
    assert_class(
        JapaneseKeystrokeAmbiguityClass
        .GEOMETRIC_SYMBOL,
        "■",
        "●",
        "◆",
        "◇",
        "□",
        "▲",
        "▼",
        "▽",
        "△",
        "◎",
        "━",
        "─",
        "│",
        "├",
    )


def test_classifies_decorative_symbols() -> None:
    assert_class(
        JapaneseKeystrokeAmbiguityClass
        .DECORATIVE_SYMBOL,
        "※",
        "♪",
        "♩",
        "♬",
        "☆",
        "★",
        "♡",
        "♥",
        "❤",
        "✨",
    )


def test_keeps_unresolved_other_cases_other() -> None:
    assert_class(
        JapaneseKeystrokeAmbiguityClass
        .OTHER,
        "",
        "∀",
        "◯",
        "〒",
        "(*´∀｀)",
    )


def test_does_not_classify_multi_character_span_by_member() -> None:
    assert_class(
        JapaneseKeystrokeAmbiguityClass
        .OTHER,
        "Σ(￣ロ￣lll)",
        "✨✨",
        "❤❤",
        "→→",
    )


def test_wave_dash_span_keeps_input_method_priority() -> None:
    assert_class(
        JapaneseKeystrokeAmbiguityClass
        .INPUT_METHOD,
        "☆〜",
        "〜→",
        "な〜",
    )

def test_classifies_invalid_source_spans() -> None:
    assert_class(
        JapaneseKeystrokeAmbiguityClass
        .INVALID_SOURCE,
        "�",
        "��",
        "���",
        "abc�def",
    )


def test_classifies_unicode_emoji() -> None:
    assert_class(
        JapaneseKeystrokeAmbiguityClass
        .EMOJI,
        "💦",
        "😍",
        "😊",
        "🇨🇳",
        "😽💕",
        "👏🤣🤣🤣",
    )


def test_keeps_text_kaomoji_other() -> None:
    assert_class(
        JapaneseKeystrokeAmbiguityClass
        .OTHER,
        "(*´∀｀)",
        "(･∀･)",
        "^▽^",
        "Σ(￣ロ￣lll)",
    )


def test_invalid_source_takes_priority_over_emoji() -> None:
    assert_class(
        JapaneseKeystrokeAmbiguityClass
        .INVALID_SOURCE,
        "�😊",
    )
