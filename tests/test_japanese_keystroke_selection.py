import pytest

from corpus_builder.japanese_corpus_occurrence import (
    JapaneseCorpusOccurrence,
)
from corpus_builder.japanese_corpus_part import (
    JapaneseCorpusPart,
    JapaneseCorpusPartKind,
)
from corpus_builder.japanese_keystroke_context import (
    JapaneseKeystrokeContextEvidence,
    JapaneseKeystrokeStructuralRegion,
)
from corpus_builder.japanese_keystroke_selection import (
    select_japanese_corpus_occurrences,
)


def make_occurrence(
    source_text: str,
    start: int,
    end: int,
) -> JapaneseCorpusOccurrence:
    return JapaneseCorpusOccurrence(
        part=JapaneseCorpusPart(
            kind=JapaneseCorpusPartKind.AMBIGUOUS,
            source_text=source_text[start:end],
            processing_text=source_text[start:end],
        ),
        source_start=start,
        source_end=end,
    )


def make_region(
    start: int,
    end: int,
) -> JapaneseKeystrokeStructuralRegion:
    return JapaneseKeystrokeStructuralRegion(
        source_start=start,
        source_end=end,
        evidence=(
            JapaneseKeystrokeContextEvidence.KAOMOJI_STRUCTURAL
        ),
    )


def test_select_japanese_corpus_occurrences_keeps_all_without_regions() -> None:
    source = "ABC"

    occurrences = (
        make_occurrence(source, 0, 1),
        make_occurrence(source, 1, 2),
        make_occurrence(source, 2, 3),
    )

    assert select_japanese_corpus_occurrences(
        source,
        occurrences,
        excluded_regions=(),
    ) == occurrences


def test_select_japanese_corpus_occurrences_excludes_whole_structural_region() -> None:
    source = "(^○^)"

    occurrences = tuple(
        make_occurrence(
            source,
            index,
            index + 1,
        )
        for index in range(
            len(source)
        )
    )

    assert select_japanese_corpus_occurrences(
        source,
        occurrences,
        excluded_regions=(
            make_region(0, 5),
        ),
    ) == ()


def test_select_japanese_corpus_occurrences_keeps_occurrences_outside_region() -> None:
    source = "A(^○^)B"

    occurrences = tuple(
        make_occurrence(
            source,
            index,
            index + 1,
        )
        for index in range(
            len(source)
        )
    )

    result = select_japanese_corpus_occurrences(
        source,
        occurrences,
        excluded_regions=(
            make_region(1, 6),
        ),
    )

    assert tuple(
        occurrence.part.source_text
        for occurrence in result
    ) == (
        "A",
        "B",
    )


def test_select_japanese_corpus_occurrences_deduplicates_identical_regions() -> None:
    source = "A(^○^)B"

    occurrences = (
        make_occurrence(source, 0, 1),
        make_occurrence(source, 1, 6),
        make_occurrence(source, 6, 7),
    )

    region = make_region(
        1,
        6,
    )

    result = select_japanese_corpus_occurrences(
        source,
        occurrences,
        excluded_regions=(
            region,
            region,
        ),
    )

    assert tuple(
        occurrence.part.source_text
        for occurrence in result
    ) == (
        "A",
        "B",
    )


def test_select_japanese_corpus_occurrences_handles_multiple_regions() -> None:
    source = "A(^○^)B(^×^)C"

    occurrences = tuple(
        make_occurrence(
            source,
            index,
            index + 1,
        )
        for index in range(
            len(source)
        )
    )

    result = select_japanese_corpus_occurrences(
        source,
        occurrences,
        excluded_regions=(
            make_region(1, 6),
            make_region(7, 12),
        ),
    )

    assert tuple(
        occurrence.part.source_text
        for occurrence in result
    ) == (
        "A",
        "B",
        "C",
    )


def test_select_japanese_corpus_occurrences_preserves_input_order() -> None:
    source = "ABC"

    occurrences = (
        make_occurrence(source, 2, 3),
        make_occurrence(source, 0, 1),
        make_occurrence(source, 1, 2),
    )

    result = select_japanese_corpus_occurrences(
        source,
        occurrences,
        excluded_regions=(),
    )

    assert result == occurrences


def test_select_japanese_corpus_occurrences_rejects_invalid_occurrence_source() -> None:
    source = "ABC"

    occurrence = JapaneseCorpusOccurrence(
        part=JapaneseCorpusPart(
            kind=JapaneseCorpusPartKind.AMBIGUOUS,
            source_text="X",
            processing_text="X",
        ),
        source_start=0,
        source_end=1,
    )

    with pytest.raises(
        ValueError,
        match="source span does not match",
    ):
        select_japanese_corpus_occurrences(
            source,
            (occurrence,),
            excluded_regions=(),
        )


def test_select_japanese_corpus_occurrences_rejects_region_beyond_source() -> None:
    source = "ABC"

    with pytest.raises(
        ValueError,
        match="structural region exceeds source text length",
    ):
        select_japanese_corpus_occurrences(
            source,
            (),
            excluded_regions=(
                make_region(0, 4),
            ),
        )


def test_select_japanese_corpus_occurrences_rejects_left_boundary_crossing() -> None:
    source = "ABCDE"

    occurrence = make_occurrence(
        source,
        0,
        3,
    )

    with pytest.raises(
        ValueError,
        match="crosses an excluded structural region boundary",
    ):
        select_japanese_corpus_occurrences(
            source,
            (occurrence,),
            excluded_regions=(
                make_region(2, 4),
            ),
        )


def test_select_japanese_corpus_occurrences_rejects_right_boundary_crossing() -> None:
    source = "ABCDE"

    occurrence = make_occurrence(
        source,
        2,
        5,
    )

    with pytest.raises(
        ValueError,
        match="crosses an excluded structural region boundary",
    ):
        select_japanese_corpus_occurrences(
            source,
            (occurrence,),
            excluded_regions=(
                make_region(1, 4),
            ),
        )


def test_select_japanese_corpus_occurrences_allows_adjacent_regions() -> None:
    source = "ABCDEF"

    occurrences = tuple(
        make_occurrence(
            source,
            index,
            index + 1,
        )
        for index in range(
            len(source)
        )
    )

    result = select_japanese_corpus_occurrences(
        source,
        occurrences,
        excluded_regions=(
            make_region(1, 3),
            make_region(3, 5),
        ),
    )

    assert tuple(
        occurrence.part.source_text
        for occurrence in result
    ) == (
        "A",
        "F",
    )


def test_select_japanese_corpus_occurrences_rejects_overlapping_regions() -> None:
    source = "ABCDEF"

    with pytest.raises(
        ValueError,
        match="excluded structural regions must not overlap",
    ):
        select_japanese_corpus_occurrences(
            source,
            (),
            excluded_regions=(
                make_region(1, 4),
                make_region(3, 5),
            ),
        )


def test_select_japanese_corpus_occurrences_accepts_empty_occurrences() -> None:
    assert select_japanese_corpus_occurrences(
        "ABC",
        (),
        excluded_regions=(),
    ) == ()
