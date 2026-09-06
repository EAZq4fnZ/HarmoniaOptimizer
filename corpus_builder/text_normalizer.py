import unicodedata


def normalize_whitespace(
    text: str,
) -> str:
    return " ".join(
        text.split()
    )


def normalize_unicode(
    text: str,
) -> str:
    return unicodedata.normalize(
        "NFC",
        text,
    )



IGNORED_FORMAT_CHARACTERS = frozenset(
    {
        "\u200b",
        "\u200e",
        "\u202a",
        "\u202c",
        "\u2060",
        "\ufeff",
        "\ufe0e",
        "\ufe0f",
    }
)


IGNORED_COMBINING_CHARACTERS = frozenset(
    {
        "\u309a",
        "\u0306",
        "\u032e",
        "\u0308",
    }
)


EMOTICON_CYRILLIC_CHARACTERS = frozenset(
    {
        "Д",
        "д",
        "о",
        "О",
        "з",
    }
)


EMOTICON_CONTEXT_CHARACTERS = frozenset(
    {
        "(",
        ")",
        "（",
        "）",
        "ﾟ",
        "゜",
        "´",
        "｀",
        "`",
        "･",
        "・",
        "；",
        ";",
        "＾",
        "^",
        "∀",
        "ω",
        "＿",
        "_",
        "'",
        '"',
        "ヽ",
        "ﾉ",
        "ノ",
        "つ",
        "⊂",
    }
)


IGNORED_SPACING_MARK_CHARACTERS = frozenset(
    {
        "\u309b",
    }
)


def remove_ignored_format_characters(
    text: str,
) -> str:
    return "".join(
        char
        for char in text
        if char
        not in IGNORED_FORMAT_CHARACTERS
    )


def remove_ignored_combining_characters(
    text: str,
) -> str:
    return "".join(
        char
        for char in text
        if char
        not in IGNORED_COMBINING_CHARACTERS
    )


def remove_observed_emoticon_cyrillic(
    text: str,
) -> str:
    result: list[str] = []

    for index, char in enumerate(text):
        if (
            char
            not in EMOTICON_CYRILLIC_CHARACTERS
        ):
            result.append(char)
            continue

        previous_char = (
            text[index - 1]
            if index > 0
            else ""
        )

        next_char = (
            text[index + 1]
            if index + 1 < len(text)
            else ""
        )

        if (
            previous_char
            in EMOTICON_CONTEXT_CHARACTERS
            or next_char
            in EMOTICON_CONTEXT_CHARACTERS
        ):
            continue

        result.append(char)

    return "".join(result)


def remove_ignored_spacing_mark_characters(
    text: str,
) -> str:
    return "".join(
        char
        for char in text
        if char
        not in IGNORED_SPACING_MARK_CHARACTERS
    )


def normalize_text(
    text: str,
) -> str:
    return normalize_whitespace(
        remove_ignored_format_characters(
            remove_ignored_spacing_mark_characters(
                remove_ignored_combining_characters(
                    remove_observed_emoticon_cyrillic(
                        normalize_unicode(text)
                    )
                )
            )
        )
    )



def normalize_fullwidth_ascii(
    text: str,
) -> str:
    result: list[str] = []

    for char in text:
        code_point = ord(char)

        if (
            0xFF10 <= code_point <= 0xFF19
            or 0xFF21 <= code_point <= 0xFF3A
            or 0xFF41 <= code_point <= 0xFF5A
        ):
            result.append(
                chr(code_point - 0xFEE0)
            )
        else:
            result.append(char)

    return "".join(result)
