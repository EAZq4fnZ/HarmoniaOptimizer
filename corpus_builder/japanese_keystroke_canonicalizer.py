from __future__ import annotations

HARMONIA_NATIVE_CHARACTERS = frozenset(
    {
        "、",
        "。",
        "－",
    }
)


FULLWIDTH_ASCII_PUNCTUATION_MAP = {
    "！": "!",
    "＂": '"',
    "＃": "#",
    "＄": "$",
    "％": "%",
    "＆": "&",
    "＇": "'",
    "（": "(",
    "）": ")",
    "＊": "*",
    "＋": "+",
    "，": ",",
    "．": ".",
    "／": "/",
    "：": ":",
    "；": ";",
    "＜": "<",
    "＝": "=",
    "＞": ">",
    "？": "?",
    "＠": "@",
    "［": "[",
    "＼": "\\",
    "］": "]",
    "＾": "^",
    "＿": "_",
    "｀": "`",
    "｛": "{",
    "｜": "|",
    "｝": "}",
    "～": "~",
}


HALFWIDTH_JAPANESE_PUNCTUATION_MAP = {
    "｡": "。",
    "､": "、",
    "｢": "[",
    "｣": "]",
    "･": "・",
}

DIRECT_JAPANESE_BRACKET_MAP = {
    "「": "[",
    "」": "]",
}

def canonicalize_japanese_keystroke_character(
    char: str,
) -> str:
    if len(char) != 1:
        raise ValueError(
            "char must contain exactly one character"
        )

    if char in HARMONIA_NATIVE_CHARACTERS:
        return char

    fullwidth_ascii = (
        FULLWIDTH_ASCII_PUNCTUATION_MAP.get(
            char
        )
    )

    if fullwidth_ascii is not None:
        return fullwidth_ascii

    halfwidth_japanese = (
        HALFWIDTH_JAPANESE_PUNCTUATION_MAP.get(
            char
        )
    )

    if halfwidth_japanese is not None:
        return halfwidth_japanese

    direct_japanese_bracket = (
        DIRECT_JAPANESE_BRACKET_MAP.get(
            char
        )
    )

    if direct_japanese_bracket is not None:
        return direct_japanese_bracket

    return char


def canonicalize_japanese_keystroke_text(
    text: str,
) -> str:
    return "".join(
        canonicalize_japanese_keystroke_character(
            char
        )
        for char in text
    )
