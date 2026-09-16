from __future__ import annotations

from collections.abc import Iterable

from .japanese_corpus_occurrence import (
    JapaneseCorpusOccurrence,
)
from .japanese_corpus_part import (
    JapaneseCorpusPartKind,
)
from .japanese_keystroke_ambiguity import (
    classify_japanese_keystroke_ambiguity,
)
from .japanese_keystroke_context import (
    JapaneseKeystrokeStructuralRegion,
    classify_japanese_keystroke_context_at,
    find_japanese_keystroke_structural_region_at,
)
from .japanese_keystroke_policy import (
    JapaneseKeystrokePolicy,
    resolve_contextual_japanese_keystroke_policy,
)
from .japanese_source_processing_relation import (
    classify_japanese_source_processing_relation,
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


def select_japanese_corpus_occurrences_by_policy(
    source_text: str,
    occurrences: Iterable[
        JapaneseCorpusOccurrence
    ],
) -> tuple[
    JapaneseCorpusOccurrence,
    ...,
]:
    """Select occurrences using contextual Japanese keystroke policy.

    Only ambiguous corpus parts require contextual policy resolution.
    An EXCLUDE decision is converted into its exact structural source
    region and delegated to the source-span selection primitive.
    """
    occurrence_list = tuple(
        occurrences
    )

    excluded_regions: list[
        JapaneseKeystrokeStructuralRegion
    ] = []

    for occurrence in occurrence_list:
        occurrence.validate_source(
            source_text
        )

        part = occurrence.part

        if (
            part.kind
            is not JapaneseCorpusPartKind.AMBIGUOUS
        ):
            continue

        ambiguity_class = (
            classify_japanese_keystroke_ambiguity(
                part.source_text
            )
        )

        relation = (
            classify_japanese_source_processing_relation(
                part.source_text,
                part.processing_text,
            )
        )

        context_evidence = (
            classify_japanese_keystroke_context_at(
                source_text=part.source_text,
                context=source_text,
                start=occurrence.source_start,
            )
        )

        policy = (
            resolve_contextual_japanese_keystroke_policy(
                ambiguity_class=ambiguity_class,
                relation=relation,
                context_evidence=context_evidence,
            )
        )

        if policy is not JapaneseKeystrokePolicy.EXCLUDE:
            continue

        region = (
            find_japanese_keystroke_structural_region_at(
                source_text=part.source_text,
                context=source_text,
                start=occurrence.source_start,
            )
        )

        if region is None:
            raise ValueError(
                "EXCLUDE policy requires a Japanese "
                "keystroke structural region"
            )

        excluded_regions.append(
            region
        )

    return select_japanese_corpus_occurrences(
        source_text,
        occurrence_list,
        excluded_regions=excluded_regions,
    )
