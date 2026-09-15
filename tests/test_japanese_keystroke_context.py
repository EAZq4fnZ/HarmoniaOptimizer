import pytest

from corpus_builder.japanese_keystroke_context import (
    JapaneseKeystrokeContextEvidence,
    classify_japanese_keystroke_context,
    classify_japanese_keystroke_context_at,
)


@pytest.mark.parametrize(
    (
        "source_text",
        "context",
    ),
    [
        (
            "♡",
            "ありがとう♡",
        ),
        (
            "✧",
            "✧キラキラ✧",
        ),
        (
            "☟",
            "こちら（☟）",
        ),
        (
            "ノ",
            "ノヽノヽノヽノ",
        ),
    ],
)
def test_classifies_decorative_adjacency(
    source_text: str,
    context: str,
) -> None:
    assert (
        classify_japanese_keystroke_context(
            source_text=source_text,
            context=context,
        )
        is JapaneseKeystrokeContextEvidence.DECORATIVE_ADJACENT
    )


@pytest.mark.parametrize(
    (
        "source_text",
        "context",
    ),
    [
        (
            "○",
            "（^○^）",
        ),
        (
            "×",
            "（^×^）",
        ),
        (
            "_",
            "（×_×）",
        ),
        (
            "▽",
            "（^▽^）",
        ),
        (
            "∀",
            "（^∀^）",
        ),
    ],
)
def test_classifies_face_pair_as_kaomoji_structural(
    source_text: str,
    context: str,
) -> None:
    assert (
        classify_japanese_keystroke_context(
            source_text=source_text,
            context=context,
        )
        is JapaneseKeystrokeContextEvidence.KAOMOJI_STRUCTURAL
    )


@pytest.mark.parametrize(
    (
        "source_text",
        "context",
    ),
    [
        (
            "α",
            "α波について説明します。",
        ),
        (
            "×",
            "3×4=12",
        ),
        (
            "○",
            "正解は○です。",
        ),
        (
            "〜",
            "営業時間は9時〜17時です。",
        ),
        (
            "〆",
            "申込〆切は明日です。",
        ),
        (
            "￥",
            "価格は￥1000です。",
        ),
        (
            "・",
            "パイレーツ・オブ・カリビアン",
        ),
        (
            "※",
            "注記（※2）です。",
        ),
        (
            "♀",
            "性別（♀）",
        ),
        (
            "↓",
            "以下（↓）",
        ),
    ],
)
def test_does_not_classify_semantic_context_as_structural(
    source_text: str,
    context: str,
) -> None:
    assert (
        classify_japanese_keystroke_context(
            source_text=source_text,
            context=context,
        )
        is not JapaneseKeystrokeContextEvidence.KAOMOJI_STRUCTURAL
    )


def test_decorative_adjacency_is_weaker_than_structural(
) -> None:
    assert (
        classify_japanese_keystroke_context(
            source_text="♡",
            context="ありがとう♡",
        )
        is JapaneseKeystrokeContextEvidence.DECORATIVE_ADJACENT
    )

    assert (
        classify_japanese_keystroke_context(
            source_text="○",
            context="（^○^）♡",
        )
        is JapaneseKeystrokeContextEvidence.KAOMOJI_STRUCTURAL
    )


def test_returns_none_when_source_is_not_in_context(
) -> None:
    assert (
        classify_japanese_keystroke_context(
            source_text="♡",
            context="通常の文章です。",
        )
        is JapaneseKeystrokeContextEvidence.NONE
    )


def test_returns_none_for_empty_source(
) -> None:
    assert (
        classify_japanese_keystroke_context(
            source_text="",
            context="（╹◡╹）♡",
        )
        is JapaneseKeystrokeContextEvidence.NONE
    )


def test_context_evidence_does_not_define_policy(
) -> None:
    evidence = classify_japanese_keystroke_context(
        source_text="○",
        context="（^○^）",
    )

    assert (
        evidence
        is JapaneseKeystrokeContextEvidence.KAOMOJI_STRUCTURAL
    )


def test_explicit_occurrence_can_distinguish_same_source_text(
) -> None:
    context = (
        "正解は○です。"
        "かなり離れた通常文です。"
        "（^○^）♡"
    )

    first_start = context.index(
        "○"
    )
    second_start = context.index(
        "○",
        first_start + 1,
    )

    assert (
        classify_japanese_keystroke_context_at(
            source_text="○",
            context=context,
            start=first_start,
        )
        is JapaneseKeystrokeContextEvidence.NONE
    )

    assert (
        classify_japanese_keystroke_context_at(
            source_text="○",
            context=context,
            start=second_start,
        )
        is JapaneseKeystrokeContextEvidence.KAOMOJI_STRUCTURAL
    )


@pytest.mark.parametrize(
    "start",
    [
        -1,
        100,
    ],
)
def test_explicit_occurrence_rejects_invalid_start(
    start: int,
) -> None:
    assert (
        classify_japanese_keystroke_context_at(
            source_text="○",
            context="正解は○です。",
            start=start,
        )
        is JapaneseKeystrokeContextEvidence.NONE
    )


def test_explicit_occurrence_rejects_non_matching_span(
) -> None:
    assert (
        classify_japanese_keystroke_context_at(
            source_text="○",
            context="正解は×です。",
            start=3,
        )
        is JapaneseKeystrokeContextEvidence.NONE
    )




@pytest.mark.parametrize(
    (
        "source_text",
        "context",
    ),
    [
        (
            "」",
            "（「(ﾟ∀ﾟ)」と「('Д`)」）",
        ),
        (
            "「",
            "（「(ﾟ∀ﾟ)」と「('Д`)」）",
        ),
    ],
)
def test_does_not_bridge_nested_kaomoji_enclosures(
    source_text: str,
    context: str,
) -> None:
    start = context.index(
        source_text
    )

    assert (
        classify_japanese_keystroke_context_at(
            source_text=source_text,
            context=context,
            start=start,
        )
        is not JapaneseKeystrokeContextEvidence.KAOMOJI_STRUCTURAL
    )


@pytest.mark.parametrize(
    (
        "source_text",
        "context",
    ),
    [
        (
            "∀",
            "(ﾟ∀ﾟ)",
        ),
        (
            "○",
            "（^○^）",
        ),
        (
            "×",
            "（^×^）",
        ),
        (
            "_",
            "（×_×）",
        ),
    ],
)
def test_structural_target_remains_inside_single_enclosure(
    source_text: str,
    context: str,
) -> None:
    start = context.index(
        source_text
    )

    assert (
        classify_japanese_keystroke_context_at(
            source_text=source_text,
            context=context,
            start=start,
        )
        is JapaneseKeystrokeContextEvidence.KAOMOJI_STRUCTURAL
    )


def test_ordinary_parenthetical_is_not_structural(
) -> None:
    context = "（老廃物・活性酸素など）"

    start = context.index(
        "・"
    )

    assert (
        classify_japanese_keystroke_context_at(
            source_text="・",
            context=context,
            start=start,
        )
        is not JapaneseKeystrokeContextEvidence.KAOMOJI_STRUCTURAL
    )
