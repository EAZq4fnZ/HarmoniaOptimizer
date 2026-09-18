# corpus_builder/japanese_keystroke_inventory.py

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass

from .japanese_corpus_occurrence import (
    JapaneseCorpusOccurrence,
)
from .japanese_corpus_part import (
    JapaneseCorpusPartKind,
)
from .japanese_keystroke_ambiguity import (
    JapaneseKeystrokeAmbiguityClass,
    classify_japanese_keystroke_ambiguity,
)
from .japanese_keystroke_context import (
    JapaneseKeystrokeContextEvidence,
    classify_japanese_keystroke_context_at,
)
from .japanese_preprocessor import (
    normalize_japanese_source_text,
)
from .japanese_source_processing_relation import (
    JapaneseSourceProcessingRelation,
    classify_japanese_source_processing_relation,
)


@dataclass(frozen=True, slots=True)
class JapaneseKeystrokeInventoryRow:
    source_text: str
    processing_text: str
    ambiguity_class: JapaneseKeystrokeAmbiguityClass
    relation: JapaneseSourceProcessingRelation
    evidence: JapaneseKeystrokeContextEvidence
    occurrence_count: int
    document_count: int


@dataclass(frozen=True, slots=True)
class JapaneseKeystrokeInventoryResult:
    document_count: int
    total_occurrences: int
    ambiguous_occurrences: int
    rows: tuple[
        JapaneseKeystrokeInventoryRow,
        ...,
    ]


type _InventoryKey = tuple[
    str,
    str,
    JapaneseKeystrokeAmbiguityClass,
    JapaneseSourceProcessingRelation,
    JapaneseKeystrokeContextEvidence,
]


def audit_japanese_keystroke_inventory(
    texts: Iterable[str],
    *,
    occurrence_reader: Callable[
        [str],
        Iterable[JapaneseCorpusOccurrence],
    ],
) -> JapaneseKeystrokeInventoryResult:
    document_count = 0
    total_occurrences = 0
    ambiguous_occurrences = 0

    occurrence_counts: dict[
        _InventoryKey,
        int,
    ] = defaultdict(int)

    document_counts: dict[
        _InventoryKey,
        int,
    ] = defaultdict(int)

    for text in texts:
        document_count += 1

        normalized = normalize_japanese_source_text(
            text
        )

        document_keys: set[
            _InventoryKey
        ] = set()

        for occurrence in occurrence_reader(
            normalized
        ):
            total_occurrences += 1

            occurrence.validate_source(
                normalized
            )

            part = occurrence.part

            if (
                part.kind
                is not JapaneseCorpusPartKind.AMBIGUOUS
            ):
                continue

            ambiguous_occurrences += 1

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

            evidence = (
                classify_japanese_keystroke_context_at(
                    source_text=part.source_text,
                    context=normalized,
                    start=occurrence.source_start,
                )
            )

            key: _InventoryKey = (
                part.source_text,
                part.processing_text,
                ambiguity_class,
                relation,
                evidence,
            )

            occurrence_counts[key] += 1
            document_keys.add(key)

        for key in document_keys:
            document_counts[key] += 1

    rows = tuple(
        JapaneseKeystrokeInventoryRow(
            source_text=source_text,
            processing_text=processing_text,
            ambiguity_class=ambiguity_class,
            relation=relation,
            evidence=evidence,
            occurrence_count=(
                occurrence_counts[key]
            ),
            document_count=(
                document_counts[key]
            ),
        )
        for key in occurrence_counts
        for (
            source_text,
            processing_text,
            ambiguity_class,
            relation,
            evidence,
        ) in (key,)
    )

    return JapaneseKeystrokeInventoryResult(
        document_count=document_count,
        total_occurrences=total_occurrences,
        ambiguous_occurrences=ambiguous_occurrences,
        rows=rows,
    )
