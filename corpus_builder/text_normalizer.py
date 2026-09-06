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


def normalize_text(
    text: str,
) -> str:
    return normalize_whitespace(
        remove_ignored_format_characters(
            remove_ignored_combining_characters(
                normalize_unicode(text)
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
