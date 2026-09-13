from corpus_builder.japanese_keystroke_ambiguity import (
    JapaneseKeystrokeAmbiguityClass,
    classify_japanese_keystroke_ambiguity,
)


def test_classifies_japanese_punctuation() -> None:
    for source_text in (
        "「",
        "」",
        "『",
        "』",
        "【",
        "】",
        "・",
        "…",
    ):
        assert (
            classify_japanese_keystroke_ambiguity(
                source_text
            )
            is JapaneseKeystrokeAmbiguityClass
            .JAPANESE_PUNCTUATION
        )


def test_classifies_wave_dash_input_method() -> None:
    for source_text in (
        "〜",
        "な〜",
        "ね〜",
        "よ〜",
        "です〜",
        "で〜",
        "も〜",
    ):
        assert (
            classify_japanese_keystroke_ambiguity(
                source_text
            )
            is JapaneseKeystrokeAmbiguityClass
            .INPUT_METHOD
        )


def test_classifies_semantic_symbols() -> None:
    for source_text in (
        "α",
        "β",
        "μ",
        "Σ",
        "×",
        "○",
        "￥",
        "〆",
    ):
        assert (
            classify_japanese_keystroke_ambiguity(
                source_text
            )
            is JapaneseKeystrokeAmbiguityClass
            .SEMANTIC_SYMBOL
        )


def test_classifies_technical_compatibility() -> None:
    for source_text in (
        "℃",
        "㎡",
        "㎏",
        "㎞",
        "㎝",
        "²",
        "³",
    ):
        assert (
            classify_japanese_keystroke_ambiguity(
                source_text
            )
            is JapaneseKeystrokeAmbiguityClass
            .COMPATIBILITY
        )


def test_classifies_circled_digits_as_compatibility() -> None:
    for source_text in (
        "①",
        "②",
        "⑩",
        "⑳",
    ):
        assert (
            classify_japanese_keystroke_ambiguity(
                source_text
            )
            is JapaneseKeystrokeAmbiguityClass
            .COMPATIBILITY
        )


def test_classifies_roman_numerals_as_compatibility() -> None:
    for source_text in (
        "Ⅰ",
        "Ⅱ",
        "Ⅸ",
        "ⅰ",
        "ⅷ",
    ):
        assert (
            classify_japanese_keystroke_ambiguity(
                source_text
            )
            is JapaneseKeystrokeAmbiguityClass
            .COMPATIBILITY
        )


def test_keeps_unresolved_other_cases_other() -> None:
    for source_text in (
        "",
        "♪",
        "☆",
        "♡",
        "→",
        "�",
        "😊",
        "(*´∀｀)",
    ):
        assert (
            classify_japanese_keystroke_ambiguity(
                source_text
            )
            is JapaneseKeystrokeAmbiguityClass
            .OTHER
        )


def test_does_not_use_semantic_symbol_blacklist_for_kaomoji() -> None:
    assert (
        classify_japanese_keystroke_ambiguity(
            "Σ(￣ロ￣lll)"
        )
        is JapaneseKeystrokeAmbiguityClass
        .OTHER
    )
