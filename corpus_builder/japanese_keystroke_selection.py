from __future__ import annotations

from collections.abc import Iterable

from .japanese_corpus_occurrence import (
    JapaneseCorpusOccurrence,
)
from .japanese_keystroke_context import (
    JapaneseKeystrokeStructuralRegion,
)


def _normalize_excluded_regions(
    regions: Iterable[
        JapaneseKeystrokeStructuralRegion
    ],
    *,
    source_length: int,
) -> tuple[
    JapaneseKeystrokeStructuralRegion,
    ...,
]:
    unique_regions: dict[
        tuple[int, int],
        JapaneseKeystrokeStructuralRegion,
    ] = {}

    for region in regions:
        if region.source_end > source_length:
            raise ValueError(
                "structural region exceeds source text length"
            )

        key = (
            region.source_start,
            region.source_end,
        )

        unique_regions.setdefault(
            key,
            region,
        )

    ordered_regions = sorted(
        unique_regions.values(),
        key=lambda region: (
            region.source_start,
            region.source_end,
        ),
    )

    previous: (
        JapaneseKeystrokeStructuralRegion
        | None
    ) = None

    for region in ordered_regions:
        if (
            previous is not None
            and region.source_start
            < previous.source_end
        ):
            raise ValueError(
                "excluded structural regions must not overlap"
            )

        previous = region

    return tuple(
        ordered_regions
    )


def _is_occurrence_inside_region(
    occurrence: JapaneseCorpusOccurrence,
    region: JapaneseKeystrokeStructuralRegion,
) -> bool:
    return (
        region.source_start
        <= occurrence.source_start
        and occurrence.source_end
        <= region.source_end
    )


def _occurrence_overlaps_region(
    occurrence: JapaneseCorpusOccurrence,
    region: JapaneseKeystrokeStructuralRegion,
) -> bool:
    return (
        occurrence.source_start
        < region.source_end
        and region.source_start
        < occurrence.source_end
    )


def select_japanese_corpus_occurrences(
    source_text: str,
    occurrences: Iterable[
        JapaneseCorpusOccurrence
    ],
    *,
    excluded_regions: Iterable[
        JapaneseKeystrokeStructuralRegion
    ],
) -> tuple[
    JapaneseCorpusOccurrence,
    ...,
]:
    """Select occurrences outside explicitly excluded source regions.

    This function performs source-span selection only. It does not
    classify context, resolve keystroke policy, romanize text, or
    canonicalize punctuation.
    """
    occurrence_list = tuple(
        occurrences
    )

    for occurrence in occurrence_list:
        occurrence.validate_source(
            source_text
        )

    regions = _normalize_excluded_regions(
        excluded_regions,
        source_length=len(source_text),
    )

    selected: list[
        JapaneseCorpusOccurrence
    ] = []

    for occurrence in occurrence_list:
        excluded = False

        for region in regions:
            if (
                occurrence.source_end
                <= region.source_start
            ):
                break

            if (
                region.source_end
                <= occurrence.source_start
            ):
                continue

            if _is_occurrence_inside_region(
                occurrence,
                region,
            ):
                excluded = True
                break

            if _occurrence_overlaps_region(
                occurrence,
                region,
            ):
                raise ValueError(
                    "Japanese corpus occurrence crosses "
                    "an excluded structural region boundary"
                )

        if not excluded:
            selected.append(
                occurrence
            )

    return tuple(
        selected
    )
