from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from .sudachi_reader import (
    SudachiMorpheme,
    SudachiTokenizer,
    select_sudachi_corpus_part,
)


@dataclass(frozen=True, slots=True)
class JapaneseAuditIssue:
    surface: str
    reading: str
    part_of_speech: str
    context: str
    error: str
    count: int = 1


@dataclass(frozen=True, slots=True)
class JapaneseAuditResult:
    total_morphemes: int
    successful_morphemes: int
    failed_morphemes: int
    issues: tuple[JapaneseAuditIssue, ...]


def audit_japanese_morphemes(
    morphemes: Iterable[SudachiMorpheme],
    *,
    romanizer: Callable[[str], str],
    context: str,
) -> JapaneseAuditResult:
    total_morphemes = 0
    successful_morphemes = 0
    failed_morphemes = 0

    issue_counts: dict[
        tuple[str, str, str, str],
        tuple[str, int],
    ] = {}

    for morpheme in morphemes:
        surface = morpheme.surface()
        reading = select_sudachi_corpus_part(
            morpheme
        )

        if reading is None:
            continue

        total_morphemes += 1

        part_of_speech = morpheme.part_of_speech()
        part_of_speech_name = part_of_speech[0]

        try:
            romanizer(reading)
        except ValueError as error:
            failed_morphemes += 1

            error_message = str(error)

            key = (
                surface,
                reading,
                part_of_speech_name,
                error_message,
            )

            previous = issue_counts.get(key)

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

            continue

        successful_morphemes += 1

    issues = tuple(
        JapaneseAuditIssue(
            surface=surface,
            reading=reading,
            part_of_speech=part_of_speech,
            context=context,
            error=error,
            count=count,
        )
        for (
            surface,
            reading,
            part_of_speech,
            error,
        ), (
            context,
            count,
        ) in issue_counts.items()
    )

    return JapaneseAuditResult(
        total_morphemes=total_morphemes,
        successful_morphemes=successful_morphemes,
        failed_morphemes=failed_morphemes,
        issues=issues,
    )



def audit_japanese_text(
    text: str,
    *,
    tokenizer: SudachiTokenizer,
    romanizer: Callable[[str], str],
) -> JapaneseAuditResult:
    return audit_japanese_morphemes(
        tokenizer.tokenize(text),
        romanizer=romanizer,
        context=text,
    )



def merge_japanese_audit_results(
    results: Iterable[JapaneseAuditResult],
) -> JapaneseAuditResult:
    total_morphemes = 0
    successful_morphemes = 0
    failed_morphemes = 0

    issue_counts: dict[
        tuple[str, str, str, str],
        tuple[str, int],
    ] = {}

    for result in results:
        total_morphemes += result.total_morphemes
        successful_morphemes += (
            result.successful_morphemes
        )
        failed_morphemes += result.failed_morphemes

        for issue in result.issues:
            key = (
                issue.surface,
                issue.reading,
                issue.part_of_speech,
                issue.error,
            )

            previous = issue_counts.get(key)

            if previous is None:
                issue_counts[key] = (
                    issue.context,
                    issue.count,
                )
            else:
                first_context, count = previous
                issue_counts[key] = (
                    first_context,
                    count + issue.count,
                )

    issues = tuple(
        JapaneseAuditIssue(
            surface=surface,
            reading=reading,
            part_of_speech=part_of_speech,
            context=context,
            error=error,
            count=count,
        )
        for (
            surface,
            reading,
            part_of_speech,
            error,
        ), (
            context,
            count,
        ) in issue_counts.items()
    )

    return JapaneseAuditResult(
        total_morphemes=total_morphemes,
        successful_morphemes=successful_morphemes,
        failed_morphemes=failed_morphemes,
        issues=issues,
    )



def audit_japanese_texts(
    texts: Iterable[str],
    *,
    tokenizer: SudachiTokenizer,
    romanizer: Callable[[str], str],
) -> JapaneseAuditResult:
    return merge_japanese_audit_results(
        audit_japanese_text(
            text,
            tokenizer=tokenizer,
            romanizer=romanizer,
        )
        for text in texts
        if text.strip()
    )
