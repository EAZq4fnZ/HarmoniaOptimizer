from __future__ import annotations

from enum import Enum


class JapaneseKeystrokeAmbiguityClass(
    str,
    Enum,
):
    JAPANESE_PUNCTUATION = (
        "japanese_punctuation"
    )
    INPUT_METHOD = "input_method"
    SEMANTIC_SYMBOL = "semantic_symbol"
    COMPATIBILITY = "compatibility"
    TYPOGRAPHIC = "typographic"
    DIRECTIONAL_SYMBOL = "directional_symbol"
    GEOMETRIC_SYMBOL = "geometric_symbol"
    DECORATIVE_SYMBOL = "decorative_symbol"
    OTHER = "other"


JAPANESE_PUNCTUATION_CHARACTERS = frozenset(
    {
        "「",
        "」",
        "『",
        "』",
        "【",
        "】",
        "〈",
        "〉",
        "《",
        "》",
        "〔",
        "〕",
        "〝",
        "〟",
        "・",
        "…",
        "‥",
    }
)


SEMANTIC_SYMBOL_CHARACTERS = frozenset(
    {
        "α",
        "β",
        "γ",
        "μ",
        "θ",
        "φ",
        "Δ",
        "Σ",
        "×",
        "○",
        "￥",
        "〆",
    }
)


TECHNICAL_COMPATIBILITY_CHARACTERS = frozenset(
    {
        "℃",
        "㎡",
        "㎏",
        "㎞",
        "㎝",
        "㎜",
        "㎎",
        "㎥",
        "ℓ",
        "㌔",
        "㍍",
        "㍉",
        "²",
        "³",
        "⁰",
    }
)


TYPOGRAPHIC_CHARACTERS = frozenset(
    {
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
        "¨",
        "˘",
    }
)


DIRECTIONAL_SYMBOL_CHARACTERS = frozenset(
    {
        "→",
        "←",
        "↑",
        "↓",
        "⇒",
        "▶",
    }
)


GEOMETRIC_SYMBOL_CHARACTERS = frozenset(
    {
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
    }
)


DECORATIVE_SYMBOL_CHARACTERS = frozenset(
    {
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
    }
)


def _is_circled_digit(
    character: str,
) -> bool:
    code_point = ord(character)

    return (
        0x2460
        <= code_point
        <= 0x2473
    )


def _is_roman_numeral(
    character: str,
) -> bool:
    code_point = ord(character)

    return (
        0x2160
        <= code_point
        <= 0x217F
    )


def _is_compatibility_character(
    character: str,
) -> bool:
    return (
        character
        in TECHNICAL_COMPATIBILITY_CHARACTERS
        or _is_circled_digit(
            character
        )
        or _is_roman_numeral(
            character
        )
    )


def classify_japanese_keystroke_ambiguity(
    source_text: str,
) -> JapaneseKeystrokeAmbiguityClass:
    if "〜" in source_text:
        return (
            JapaneseKeystrokeAmbiguityClass
            .INPUT_METHOD
        )

    if (
        source_text
        in JAPANESE_PUNCTUATION_CHARACTERS
    ):
        return (
            JapaneseKeystrokeAmbiguityClass
            .JAPANESE_PUNCTUATION
        )

    if (
        source_text
        in SEMANTIC_SYMBOL_CHARACTERS
    ):
        return (
            JapaneseKeystrokeAmbiguityClass
            .SEMANTIC_SYMBOL
        )

    if (
        len(source_text) == 1
        and _is_compatibility_character(
            source_text
        )
    ):
        return (
            JapaneseKeystrokeAmbiguityClass
            .COMPATIBILITY
        )

    if source_text in TYPOGRAPHIC_CHARACTERS:
        return (
            JapaneseKeystrokeAmbiguityClass
            .TYPOGRAPHIC
        )

    if (
        source_text
        in DIRECTIONAL_SYMBOL_CHARACTERS
    ):
        return (
            JapaneseKeystrokeAmbiguityClass
            .DIRECTIONAL_SYMBOL
        )

    if (
        source_text
        in GEOMETRIC_SYMBOL_CHARACTERS
    ):
        return (
            JapaneseKeystrokeAmbiguityClass
            .GEOMETRIC_SYMBOL
        )

    if (
        source_text
        in DECORATIVE_SYMBOL_CHARACTERS
    ):
        return (
            JapaneseKeystrokeAmbiguityClass
            .DECORATIVE_SYMBOL
        )

    return (
        JapaneseKeystrokeAmbiguityClass
        .OTHER
    )
