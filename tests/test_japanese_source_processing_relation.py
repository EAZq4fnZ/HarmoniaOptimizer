import pytest

from corpus_builder.japanese_source_processing_relation import (
    JapaneseSourceProcessingRelation,
    classify_japanese_source_processing_relation,
)


@pytest.mark.parametrize(
    (
        "source_text",
        "processing_text",
    ),
    [
        ("α", "α"),
        ("〜", "〜"),
        ("〇", "〇"),
        ("Python", "Python"),
    ],
)
def test_classify_identical_relation(
    source_text: str,
    processing_text: str,
) -> None:
    assert (
        classify_japanese_source_processing_relation(
            source_text,
            processing_text,
        )
        is JapaneseSourceProcessingRelation.IDENTICAL
    )


@pytest.mark.parametrize(
    (
        "source_text",
        "processing_text",
    ),
    [
        ("！", "!"),
        ("（", "("),
        ("）", ")"),
        ("-*）", "-*)"),
        (";＞_＜;)", ";>_<;)"),
        ("！✌#", "!✌#"),
        ("（╹◡╹）♡", "(╹◡╹)♡"),
        ("（☟", "(☟"),
        ("❤＼(^", "❤\\(^"),
    ],
)
def test_classify_canonicalized_relation(
    source_text: str,
    processing_text: str,
) -> None:
    assert (
        classify_japanese_source_processing_relation(
            source_text,
            processing_text,
        )
        is (
            JapaneseSourceProcessingRelation
            .CANONICALIZED
        )
    )


@pytest.mark.parametrize(
    (
        "source_text",
        "processing_text",
    ),
    [
        ("´", " "),
        ("￣", " "),
        ("´", ""),
    ],
)
def test_classify_lossy_relation(
    source_text: str,
    processing_text: str,
) -> None:
    assert (
        classify_japanese_source_processing_relation(
            source_text,
            processing_text,
        )
        is JapaneseSourceProcessingRelation.LOSSY
    )


@pytest.mark.parametrize(
    (
        "source_text",
        "processing_text",
    ),
    [
        ("℃", "ド"),
        ("α", "アルファー"),
        ("β", "ベータ"),
        ("Σ", "シグマ"),
        ("〆", "シメ"),
        ("〆切", "シメキリ"),
        ("㎏", "キログラム"),
        ("㎏", "ケージー"),
        ("μm", "マイクロメートル"),
        ("¥", "エン"),
        ("な〜", "ナ"),
        ("ど〜", "ドウ"),
        ("な〜ん", "ナニ"),
        ("ち○ぽ", "チンポ"),
    ],
)
def test_classify_linguistic_reading_relation(
    source_text: str,
    processing_text: str,
) -> None:
    assert (
        classify_japanese_source_processing_relation(
            source_text,
            processing_text,
        )
        is (
            JapaneseSourceProcessingRelation
            .LINGUISTIC_READING
        )
    )


@pytest.mark.parametrize(
    (
        "source_text",
        "processing_text",
    ),
    [
        ("㎡", "m2"),
        ("Τάμα", "τάμα"),
        ("✧", "..✧"),
        ("abc", "ABC"),
        (" ", ""),
    ],
)
def test_classify_unresolved_relation(
    source_text: str,
    processing_text: str,
) -> None:
    assert (
        classify_japanese_source_processing_relation(
            source_text,
            processing_text,
        )
        is JapaneseSourceProcessingRelation.UNRESOLVED
    )


def test_identical_relation_takes_priority_over_reading_detection(
) -> None:
    assert (
        classify_japanese_source_processing_relation(
            "カタカナ",
            "カタカナ",
        )
        is JapaneseSourceProcessingRelation.IDENTICAL
    )


def test_canonicalized_relation_takes_priority_over_other_relations(
) -> None:
    assert (
        classify_japanese_source_processing_relation(
            "！",
            "!",
        )
        is (
            JapaneseSourceProcessingRelation
            .CANONICALIZED
        )
    )
