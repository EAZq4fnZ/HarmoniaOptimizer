import pytest

from corpus_builder.japanese_corpus_builder import (
    build_japanese_corpus,
)


def test_build_japanese_corpus_builds_processed_result() -> None:
    result = build_japanese_corpus(
        (
            "今日は晴れです。",
            "明日も晴れです。",
        ),
        reader=lambda text: text,
        romanizer=lambda text: "abc",
    )

    assert result.category == "japanese"
    assert result.source_document_count == 2
    assert result.text == "abc abc"
    assert result.ascii_letter_count == 6


def test_build_japanese_corpus_rejects_empty_documents() -> None:
    with pytest.raises(
        ValueError,
        match="documents must not be empty",
    ):
        build_japanese_corpus(
            (),
            reader=lambda text: text,
            romanizer=lambda text: "abc",
        )


def test_build_japanese_corpus_rejects_empty_document() -> None:
    with pytest.raises(
        ValueError,
        match="document must not be empty",
    ):
        build_japanese_corpus(
            (
                "今日は晴れです。",
                "",
            ),
            reader=lambda text: text,
            romanizer=lambda text: "abc",
        )

def test_build_japanese_corpus_with_default_japanese_pipeline() -> None:
    from corpus_builder.japanese_reader import (
        make_default_japanese_reader,
    )
    from corpus_builder.japanese_romanizer import (
        romanize_japanese_reading,
    )

    result = build_japanese_corpus(
        (
            "今日は晴れです。",
            "明日も晴れです。",
        ),
        reader=make_default_japanese_reader(),
        romanizer=romanize_japanese_reading,
    )

    assert result.category == "japanese"
    assert result.source_document_count == 2
    assert result.ascii_letter_count > 0
    assert result.text


def test_build_japanese_corpus_with_structured_pipeline() -> None:
    from corpus_builder.japanese_keystroke_canonicalizer import (
        canonicalize_japanese_keystroke_text,
    )
    from corpus_builder.japanese_reader import (
        make_default_japanese_reader,
    )
    from corpus_builder.japanese_romanizer import (
        romanize_japanese_reading,
    )

    reader = make_default_japanese_reader()

    result = build_japanese_corpus(
        (
            "今日はPython！〇",
            "ＡＢＣ今日は良い天気です。",
        ),
        part_reader=reader.read_parts,
        romanizer=romanize_japanese_reading,
        canonicalizer=(
            canonicalize_japanese_keystroke_text
        ),
    )

    assert result.category == "japanese"
    assert result.source_document_count == 2
    assert result.text == (
        "kyouhaPython!maru "
        "ABCkyouhayoitennkidesu。"
    )


def test_build_japanese_corpus_structured_pipeline_rejects_ambiguous_part() -> None:
    from corpus_builder.japanese_keystroke_canonicalizer import (
        canonicalize_japanese_keystroke_text,
    )
    from corpus_builder.japanese_reader import (
        make_default_japanese_reader,
    )
    from corpus_builder.japanese_romanizer import (
        romanize_japanese_reading,
    )

    reader = make_default_japanese_reader()

    with pytest.raises(
        ValueError,
        match="ambiguous Japanese corpus part",
    ):
        build_japanese_corpus(
            ("ど〜",),
            part_reader=reader.read_parts,
            romanizer=romanize_japanese_reading,
            canonicalizer=(
                canonicalize_japanese_keystroke_text
            ),
        )


def test_build_japanese_corpus_requires_part_reader_for_structured_pipeline() -> None:
    with pytest.raises(
        ValueError,
        match="part_reader is required",
    ):
        build_japanese_corpus(
            ("今日は晴れです。",),
            romanizer=lambda text: text,
            canonicalizer=lambda text: text,
        )


def test_build_japanese_corpus_requires_romanizer_for_structured_pipeline() -> None:
    with pytest.raises(
        ValueError,
        match="romanizer is required",
    ):
        build_japanese_corpus(
            ("今日は晴れです。",),
            part_reader=lambda text: (),
            canonicalizer=lambda text: text,
        )


def test_build_japanese_corpus_requires_canonicalizer_for_structured_pipeline() -> None:
    with pytest.raises(
        ValueError,
        match="canonicalizer is required",
    ):
        build_japanese_corpus(
            ("今日は晴れです。",),
            part_reader=lambda text: (),
            romanizer=lambda text: text,
        )


def test_build_japanese_corpus_with_occurrence_aware_pipeline() -> None:
    from corpus_builder.japanese_keystroke_canonicalizer import (
        canonicalize_japanese_keystroke_text,
    )
    from corpus_builder.japanese_reader import (
        make_default_japanese_reader,
    )
    from corpus_builder.japanese_romanizer import (
        romanize_japanese_reading,
    )

    reader = make_default_japanese_reader()

    result = build_japanese_corpus(
        (
            "今日はPython！〇",
            "Ａ(^○^)Ｂ",
        ),
        occurrence_reader=reader.read_occurrences,
        romanizer=romanize_japanese_reading,
        canonicalizer=(
            canonicalize_japanese_keystroke_text
        ),
    )

    assert result.category == "japanese"
    assert result.source_document_count == 2
    assert result.text == (
        "kyouhaPython!maru AB"
    )


def test_build_japanese_corpus_occurrence_pipeline_skips_excluded_document() -> None:
    from corpus_builder.japanese_keystroke_canonicalizer import (
        canonicalize_japanese_keystroke_text,
    )
    from corpus_builder.japanese_reader import (
        make_default_japanese_reader,
    )
    from corpus_builder.japanese_romanizer import (
        romanize_japanese_reading,
    )

    reader = make_default_japanese_reader()

    result = build_japanese_corpus(
        (
            "今日はPython！〇",
            "(^○^)",
            "ＡＢＣ",
        ),
        occurrence_reader=reader.read_occurrences,
        romanizer=romanize_japanese_reading,
        canonicalizer=(
            canonicalize_japanese_keystroke_text
        ),
    )

    assert result.source_document_count == 3
    assert result.text == (
        "kyouhaPython!maru ABC"
    )


def test_build_japanese_corpus_occurrence_pipeline_rejects_all_excluded_documents() -> None:
    from corpus_builder.japanese_keystroke_canonicalizer import (
        canonicalize_japanese_keystroke_text,
    )
    from corpus_builder.japanese_reader import (
        make_default_japanese_reader,
    )
    from corpus_builder.japanese_romanizer import (
        romanize_japanese_reading,
    )

    reader = make_default_japanese_reader()

    with pytest.raises(
        ValueError,
        match="excluded all documents",
    ):
        build_japanese_corpus(
            (
                "(^○^)",
                "（^×^）",
            ),
            occurrence_reader=reader.read_occurrences,
            romanizer=romanize_japanese_reading,
            canonicalizer=(
                canonicalize_japanese_keystroke_text
            ),
        )


def test_build_japanese_corpus_rejects_part_and_occurrence_readers_together() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "part_reader and occurrence_reader "
            "must not be used together"
        ),
    ):
        build_japanese_corpus(
            ("今日は晴れです。",),
            part_reader=lambda text: (),
            occurrence_reader=lambda text: (),
            romanizer=lambda text: text,
            canonicalizer=lambda text: text,
        )


def test_build_japanese_corpus_requires_romanizer_for_occurrence_pipeline() -> None:
    with pytest.raises(
        ValueError,
        match="romanizer is required",
    ):
        build_japanese_corpus(
            ("今日は晴れです。",),
            occurrence_reader=lambda text: (),
            canonicalizer=lambda text: text,
        )


def test_build_japanese_corpus_requires_canonicalizer_for_occurrence_pipeline() -> None:
    with pytest.raises(
        ValueError,
        match="canonicalizer is required",
    ):
        build_japanese_corpus(
            ("今日は晴れです。",),
            occurrence_reader=lambda text: (),
            romanizer=lambda text: text,
        )
