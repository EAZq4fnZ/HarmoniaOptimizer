from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

from corpus_builder.japanese_corpus_occurrence import (
    JapaneseCorpusOccurrence,
)
from corpus_builder.japanese_corpus_part import (
    JapaneseCorpusPartKind,
)
from corpus_builder.japanese_keystroke_ambiguity import (
    JapaneseKeystrokeAmbiguityClass,
    classify_japanese_keystroke_ambiguity,
)
from corpus_builder.japanese_keystroke_audit import (
    JapaneseKeystrokeAuditResult,
)
from corpus_builder.japanese_keystroke_context import (
    JapaneseKeystrokeContextEvidence,
    classify_japanese_keystroke_context,
    classify_japanese_keystroke_context_at,
)
from corpus_builder.japanese_source_processing_relation import (
    JapaneseSourceProcessingRelation,
    classify_japanese_source_processing_relation,
)


@dataclass(frozen=True, slots=True)
class JapaneseKeystrokeContextCount:
    evidence: JapaneseKeystrokeContextEvidence
    count: int
    unique_issue_count: int


@dataclass(frozen=True, slots=True)
class JapaneseAmbiguityRelationContextCount:
    ambiguity_class: JapaneseKeystrokeAmbiguityClass
    relation: JapaneseSourceProcessingRelation
    evidence: JapaneseKeystrokeContextEvidence
    count: int
    unique_issue_count: int


@dataclass(frozen=True, slots=True)
class JapaneseKeystrokeContextAuditResult:
    total_parts: int
    ambiguous_parts: int
    context_counts: tuple[
        JapaneseKeystrokeContextCount,
        ...,
    ]
    ambiguity_relation_context_counts: tuple[
        JapaneseAmbiguityRelationContextCount,
        ...,
    ]


def _build_context_audit_result(
    *,
    total_parts: int,
    ambiguous_parts: int,
    context_counts: dict[
        JapaneseKeystrokeContextEvidence,
        int,
    ],
    context_unique_issues: dict[
        JapaneseKeystrokeContextEvidence,
        set[tuple[str, str]],
    ],
    cross_counts: dict[
        tuple[
            JapaneseKeystrokeAmbiguityClass,
            JapaneseSourceProcessingRelation,
            JapaneseKeystrokeContextEvidence,
        ],
        int,
    ],
    cross_unique_issues: dict[
        tuple[
            JapaneseKeystrokeAmbiguityClass,
            JapaneseSourceProcessingRelation,
            JapaneseKeystrokeContextEvidence,
        ],
        set[tuple[str, str]],
    ],
) -> JapaneseKeystrokeContextAuditResult:
    context_rows = tuple(
        JapaneseKeystrokeContextCount(
            evidence=evidence,
            count=context_counts[evidence],
            unique_issue_count=len(
                context_unique_issues[evidence]
            ),
        )
        for evidence in JapaneseKeystrokeContextEvidence
        if context_counts[evidence] > 0
    )

    cross_rows = tuple(
        JapaneseAmbiguityRelationContextCount(
            ambiguity_class=ambiguity_class,
            relation=relation,
            evidence=evidence,
            count=cross_counts[
                (
                    ambiguity_class,
                    relation,
                    evidence,
                )
            ],
            unique_issue_count=len(
                cross_unique_issues[
                    (
                        ambiguity_class,
                        relation,
                        evidence,
                    )
                ]
            ),
        )
        for ambiguity_class in JapaneseKeystrokeAmbiguityClass
        for relation in JapaneseSourceProcessingRelation
        for evidence in JapaneseKeystrokeContextEvidence
        if (
            cross_counts[
                (
                    ambiguity_class,
                    relation,
                    evidence,
                )
            ]
            > 0
        )
    )

    return JapaneseKeystrokeContextAuditResult(
        total_parts=total_parts,
        ambiguous_parts=ambiguous_parts,
        context_counts=context_rows,
        ambiguity_relation_context_counts=(
            cross_rows
        ),
    )


def summarize_japanese_keystroke_contexts(
    audit_result: JapaneseKeystrokeAuditResult,
) -> JapaneseKeystrokeContextAuditResult:
    """Summarize contextual evidence for ambiguity audit issues."""
    context_counts: dict[
        JapaneseKeystrokeContextEvidence,
        int,
    ] = defaultdict(int)

    context_unique_counts: dict[
        JapaneseKeystrokeContextEvidence,
        int,
    ] = defaultdict(int)

    cross_counts: dict[
        tuple[
            JapaneseKeystrokeAmbiguityClass,
            JapaneseSourceProcessingRelation,
            JapaneseKeystrokeContextEvidence,
        ],
        int,
    ] = defaultdict(int)

    cross_unique_counts: dict[
        tuple[
            JapaneseKeystrokeAmbiguityClass,
            JapaneseSourceProcessingRelation,
            JapaneseKeystrokeContextEvidence,
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

        evidence = classify_japanese_keystroke_context(
            source_text=issue.source_text,
            context=issue.context,
        )

        context_counts[
            evidence
        ] += issue.count

        context_unique_counts[
            evidence
        ] += 1

        key = (
            ambiguity_class,
            relation,
            evidence,
        )

        cross_counts[
            key
        ] += issue.count

        cross_unique_counts[
            key
        ] += 1

    context_rows = tuple(
        JapaneseKeystrokeContextCount(
            evidence=evidence,
            count=context_counts[evidence],
            unique_issue_count=(
                context_unique_counts[evidence]
            ),
        )
        for evidence in JapaneseKeystrokeContextEvidence
        if context_counts[evidence] > 0
    )

    cross_rows = tuple(
        JapaneseAmbiguityRelationContextCount(
            ambiguity_class=ambiguity_class,
            relation=relation,
            evidence=evidence,
            count=cross_counts[
                (
                    ambiguity_class,
                    relation,
                    evidence,
                )
            ],
            unique_issue_count=(
                cross_unique_counts[
                    (
                        ambiguity_class,
                        relation,
                        evidence,
                    )
                ]
            ),
        )
        for ambiguity_class in JapaneseKeystrokeAmbiguityClass
        for relation in JapaneseSourceProcessingRelation
        for evidence in JapaneseKeystrokeContextEvidence
        if (
            cross_counts[
                (
                    ambiguity_class,
                    relation,
                    evidence,
                )
            ]
            > 0
        )
    )

    return JapaneseKeystrokeContextAuditResult(
        total_parts=audit_result.total_parts,
        ambiguous_parts=audit_result.ambiguous_parts,
        context_counts=context_rows,
        ambiguity_relation_context_counts=(
            cross_rows
        ),
    )


def audit_japanese_keystroke_occurrence_contexts(
    source_text: str,
    occurrences: Iterable[
        JapaneseCorpusOccurrence
    ],
) -> JapaneseKeystrokeContextAuditResult:
    """Audit context evidence at exact Japanese corpus occurrences."""
    total_parts = 0
    ambiguous_parts = 0

    context_counts: dict[
        JapaneseKeystrokeContextEvidence,
        int,
    ] = defaultdict(int)

    context_unique_issues: dict[
        JapaneseKeystrokeContextEvidence,
        set[tuple[str, str]],
    ] = defaultdict(set)

    cross_counts: dict[
        tuple[
            JapaneseKeystrokeAmbiguityClass,
            JapaneseSourceProcessingRelation,
            JapaneseKeystrokeContextEvidence,
        ],
        int,
    ] = defaultdict(int)

    cross_unique_issues: dict[
        tuple[
            JapaneseKeystrokeAmbiguityClass,
            JapaneseSourceProcessingRelation,
            JapaneseKeystrokeContextEvidence,
        ],
        set[tuple[str, str]],
    ] = defaultdict(set)

    for occurrence in occurrences:
        total_parts += 1

        occurrence.validate_source(
            source_text
        )

        part = occurrence.part

        if (
            part.kind
            is not JapaneseCorpusPartKind.AMBIGUOUS
        ):
            continue

        ambiguous_parts += 1

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
                context=source_text,
                start=occurrence.source_start,
            )
        )

        issue_key = (
            part.source_text,
            part.processing_text,
        )

        context_counts[
            evidence
        ] += 1

        context_unique_issues[
            evidence
        ].add(
            issue_key
        )

        key = (
            ambiguity_class,
            relation,
            evidence,
        )

        cross_counts[
            key
        ] += 1

        cross_unique_issues[
            key
        ].add(
            issue_key
        )

    return _build_context_audit_result(
        total_parts=total_parts,
        ambiguous_parts=ambiguous_parts,
        context_counts=context_counts,
        context_unique_issues=context_unique_issues,
        cross_counts=cross_counts,
        cross_unique_issues=cross_unique_issues,
    )
