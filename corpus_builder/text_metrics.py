def count_ascii_letters(
    text: str,
) -> int:
    return sum(
        1
        for char in text
        if (
            "A" <= char <= "Z"
            or "a" <= char <= "z"
        )
    )
