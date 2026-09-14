from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from corpus_builder.japanese_keystroke_ambiguity import (
    JapaneseKeystrokeAmbiguityClass,
    classify_japanese_keystroke_ambiguity,
)
from corpus_builder.japanese_keystroke_audit import (
    JapaneseKeystrokeAuditResult,
)
from corpus_builder.japanese_source_processing_relation import (
    JapaneseSourceProcessingRelation,
    classify_japanese_source_processing_relation,
)


@dataclass(frozen=True, slots=True)
class JapaneseSourceProcessingRelationCount:
    relation: JapaneseSourceProcessingRelation
    count: int
    unique_issue_count: int


@dataclass(frozen=True, slots=True)
class JapaneseAmbiguityRelationCount:
    ambiguity_class: JapaneseKeystrokeAmbiguityClass
    relation: JapaneseSourceProcessingRelation
    count: int
    unique_issue_count: int


@dataclass(frozen=True, slots=True)
class JapaneseKeystrokeRelationAuditResult:
    total_parts: int
    ambiguous_parts: int
    relation_counts: tuple[
        JapaneseSourceProcessingRelationCount,
        ...,
    ]
    ambiguity_relation_counts: tuple[
        JapaneseAmbiguityRelationCount,
        ...,
    ]


def summarize_japanese_keystroke_relations(
    audit_result: JapaneseKeystrokeAuditResult,
) -> JapaneseKeystrokeRelationAuditResult:
    """Summarize source/processing relations for ambiguity audit issues."""
    relation_counts: dict[
        JapaneseSourceProcessingRelation,
        int,
    ] = defaultdict(int)

    relation_unique_counts: dict[
        JapaneseSourceProcessingRelation,
        int,
    ] = defaultdict(int)

    cross_counts: dict[
        tuple[
            JapaneseKeystrokeAmbiguityClass,
            JapaneseSourceProcessingRelation,
        ],
        int,
    ] = defaultdict(int)

    cross_unique_counts: dict[
        tuple[
            JapaneseKeystrokeAmbiguityClass,
            JapaneseSourceProcessingRelation,
        ],
        int,
    ] = defaultdict(int)

    for issue in audit_result.issues:
        ambiguity_class = (
            classify_japanese_keystroke_ambiguity(
                issue.source_text
            )
        )

        relation = (
            classify_japanese_source_processing_relation(
                issue.source_text,
                issue.processing_text,
            )
        )

        relation_counts[
            relation
        ] += issue.count

        relation_unique_counts[
            relation
        ] += 1

        key = (
            ambiguity_class,
            relation,
        )

        cross_counts[
            key
        ] += issue.count

        cross_unique_counts[
            key
        ] += 1

    relation_rows = tuple(
        JapaneseSourceProcessingRelationCount(
            relation=relation,
            count=relation_counts[relation],
            unique_issue_count=(
                relation_unique_counts[relation]
            ),
        )
        for relation in (
            JapaneseSourceProcessingRelation
        )
        if relation_counts[relation] > 0
    )

    ambiguity_relation_rows = tuple(
        JapaneseAmbiguityRelationCount(
            ambiguity_class=ambiguity_class,
            relation=relation,
            count=cross_counts[
                (
                    ambiguity_class,
                    relation,
                )
            ],
            unique_issue_count=(
                cross_unique_counts[
                    (
                        ambiguity_class,
                        relation,
                    )
                ]
            ),
        )
        for ambiguity_class in (
            JapaneseKeystrokeAmbiguityClass
        )
        for relation in (
            JapaneseSourceProcessingRelation
        )
        if (
            cross_counts[
                (
                    ambiguity_class,
                    relation,
                )
            ]
            > 0
        )
    )

    return JapaneseKeystrokeRelationAuditResult(
        total_parts=audit_result.total_parts,
        ambiguous_parts=(
            audit_result.ambiguous_parts
        ),
        relation_counts=relation_rows,
        ambiguity_relation_counts=(
            ambiguity_relation_rows
        ),
    )
