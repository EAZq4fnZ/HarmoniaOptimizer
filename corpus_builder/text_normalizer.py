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



def normalize_text(
    text: str,
) -> str:
    return normalize_whitespace(
        normalize_unicode(text)
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
