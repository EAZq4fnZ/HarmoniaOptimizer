from __future__ import annotations

from enum import Enum


class JapaneseKeystrokeContextEvidence(str, Enum):
    NONE = "none"
    DECORATIVE_ADJACENT = "decorative_adjacent"
    KAOMOJI_STRUCTURAL = "kaomoji_structural"


_DECORATIVE_CHARACTERS = frozenset(
    "♡♥❤☆★♪♫♬✧✦✩✪✌☜☞☝☟"
)

_KAOMOJI_CHARACTERS = frozenset(
    "^＾_＿;；:：(（)）"
    "ノヽヾゞ"
    "ωΩдД∀▽▼"
    "・･"
    "´｀`"
    "≧≦＞＜><"
)

_FACE_PAIR_CHARACTERS = frozenset(
    "^＾ﾟ゜≧≦＞＜><×"
    "ωΩдД∀▽▼"
)

_ENCLOSING_PAIRS = (
    ("(", ")"),
    ("（", "）"),
)

_CONTEXT_RADIUS = 8
_MAX_ENCLOSING_PAIR_DISTANCE = 12


def _find_enclosing_pair(
    *,
    context: str,
    start: int,
    end: int,
) -> tuple[int, int] | None:
    best_pair: tuple[int, int] | None = None
    best_width: int | None = None

    for left_character, right_character in (
        _ENCLOSING_PAIRS
    ):
        left_search_start = max(
            0,
            start - _MAX_ENCLOSING_PAIR_DISTANCE,
        )

        left = context.rfind(
            left_character,
            left_search_start,
            start + 1,
        )

        if left < 0:
            continue

        right_search_end = min(
            len(context),
            end + _MAX_ENCLOSING_PAIR_DISTANCE + 1,
        )

        right = context.find(
            right_character,
            end,
            right_search_end,
        )

        if right < 0:
            continue

        if not (
            left < start
            and end <= right
        ):
            continue

        width = right - left

        if (
            best_width is None
            or width < best_width
        ):
            best_pair = (
                left,
                right,
            )
            best_width = width

    return best_pair


def _has_face_pair_structure(
    *,
    source_text: str,
    context: str,
    start: int,
    end: int,
) -> bool:
    enclosing_pair = _find_enclosing_pair(
        context=context,
        start=start,
        end=end,
    )

    if enclosing_pair is None:
        return False

    left, right = enclosing_pair

    interior_start = left + 1
    interior_end = right

    left_side = context[
        interior_start:start
    ]
    right_side = context[
        end:interior_end
    ]
    if not left_side or not right_side:
        return False

    enclosing_characters = frozenset(
        character
        for pair in _ENCLOSING_PAIRS
        for character in pair
    )

    if any(
        character in enclosing_characters
        for character in (
            left_side + right_side
        )
    ):
        return False

    has_left_face_character = any(
        character in _FACE_PAIR_CHARACTERS
        for character in left_side
    )

    has_right_face_character = any(
        character in _FACE_PAIR_CHARACTERS
        for character in right_side
    )

    return (
        has_left_face_character
        and has_right_face_character
    )


def _has_decorative_adjacency(
    *,
    source_text: str,
    context: str,
    start: int,
    end: int,
) -> bool:
    if any(
        character in _DECORATIVE_CHARACTERS
        for character in source_text
    ):
        return True

    window_start = max(
        0,
        start - _CONTEXT_RADIUS,
    )
    window_end = min(
        len(context),
        end + _CONTEXT_RADIUS,
    )

    window = context[
        window_start:window_end
    ]

    if any(
        character in _DECORATIVE_CHARACTERS
        for character in window
    ):
        return True

    kaomoji_character_count = sum(
        character in _KAOMOJI_CHARACTERS
        for character in window
    )

    return kaomoji_character_count >= 3


def classify_japanese_keystroke_context_at(
    *,
    source_text: str,
    context: str,
    start: int,
) -> JapaneseKeystrokeContextEvidence:
    """Classify contextual evidence at one exact source occurrence."""
    if not source_text or not context:
        return JapaneseKeystrokeContextEvidence.NONE

    if start < 0:
        return JapaneseKeystrokeContextEvidence.NONE

    end = start + len(
        source_text
    )

    if end > len(context):
        return JapaneseKeystrokeContextEvidence.NONE

    if (
        context[start:end]
        != source_text
    ):
        return JapaneseKeystrokeContextEvidence.NONE

    if _has_face_pair_structure(
        source_text=source_text,
        context=context,
        start=start,
        end=end,
    ):
        return (
            JapaneseKeystrokeContextEvidence.KAOMOJI_STRUCTURAL
        )

    if _has_decorative_adjacency(
        source_text=source_text,
        context=context,
        start=start,
        end=end,
    ):
        return (
            JapaneseKeystrokeContextEvidence.DECORATIVE_ADJACENT
        )

    return JapaneseKeystrokeContextEvidence.NONE


def classify_japanese_keystroke_context(
    *,
    source_text: str,
    context: str,
) -> JapaneseKeystrokeContextEvidence:
    """Classify contextual evidence for the first source occurrence."""
    if not source_text or not context:
        return JapaneseKeystrokeContextEvidence.NONE

    start = context.find(
        source_text
    )

    if start < 0:
        return JapaneseKeystrokeContextEvidence.NONE

    return classify_japanese_keystroke_context_at(
        source_text=source_text,
        context=context,
        start=start,
    )
