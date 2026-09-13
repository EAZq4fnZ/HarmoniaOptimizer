from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from .japanese_corpus_part import (
    JapaneseCorpusPart,
    JapaneseCorpusPartKind,
)


@dataclass(frozen=True, slots=True)
class JapaneseKeystrokeAuditIssue:
    source_text: str
    processing_text: str
    kind: JapaneseCorpusPartKind
    context: str
    reason: str
    count: int = 1


@dataclass(frozen=True, slots=True)
class JapaneseKeystrokeAuditResult:
    total_parts: int
    ambiguous_parts: int
    issues: tuple[
        JapaneseKeystrokeAuditIssue,
        ...,
    ]


def audit_japanese_keystroke_parts(
    parts: Iterable[JapaneseCorpusPart],
    *,
    context: str,
) -> JapaneseKeystrokeAuditResult:
    total_parts = 0
    ambiguous_parts = 0

    issue_counts: dict[
        tuple[
            str,
            str,
            JapaneseCorpusPartKind,
            str,
        ],
        tuple[str, int],
    ] = {}

    for part in parts:
        total_parts += 1

        if (
            part.kind
            is not JapaneseCorpusPartKind.AMBIGUOUS
        ):
            continue

        ambiguous_parts += 1

        reason = (
            "ambiguous Japanese keystroke semantics"
        )

        key = (
            part.source_text,
            part.processing_text,
            part.kind,
            reason,
        )

        previous = issue_counts.get(
            key
        )

        if previous is None:
            issue_counts[key] = (
                context,
                1,
            )
        else:
            first_context, count = previous
            issue_counts[key] = (
                first_context,
                count + 1,
            )

    issues = tuple(
        JapaneseKeystrokeAuditIssue(
            source_text=source_text,
            processing_text=processing_text,
            kind=kind,
            context=first_context,
            reason=reason,
            count=count,
        )
        for (
            source_text,
            processing_text,
            kind,
            reason,
        ), (
            first_context,
            count,
        ) in issue_counts.items()
    )

    return JapaneseKeystrokeAuditResult(
        total_parts=total_parts,
        ambiguous_parts=ambiguous_parts,
        issues=issues,
    )
