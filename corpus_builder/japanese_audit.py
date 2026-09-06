from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from .sudachi_reader import (
    SudachiMorpheme,
    SudachiTokenizer,
    select_sudachi_corpus_part,
)
from .text_normalizer import (
    normalize_fullwidth_ascii,
    normalize_text,
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


def should_audit_japanese_part(
    surface: str,
    reading: str,
) -> bool:
    ignored_surfaces = {
        "〇",
        "×",
        "△",
        "□",
        "㈱",
        "ﾟ",
    }

    if surface in ignored_surfaces:
        return False

    for character in reading:
        code_point = ord(character)

        is_greek = (
            0x0370 <= code_point <= 0x03FF
            or 0x1F00 <= code_point <= 0x1FFF
        )

        is_cyrillic = (
            0x0400 <= code_point <= 0x052F
            or 0x1C80 <= code_point <= 0x1C8F
            or 0x2DE0 <= code_point <= 0x2DFF
            or 0xA640 <= code_point <= 0xA69F
        )

        if is_greek or is_cyrillic:
            return False

    return True

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

    parts: list[
        tuple[str, str, str]
    ] = []

    selection_failures = 0

    for morpheme in morphemes:
        surface = morpheme.surface()
        part_of_speech = morpheme.part_of_speech()
        part_of_speech_name = part_of_speech[0]

        try:
            reading = select_sudachi_corpus_part(
                morpheme
            )
        except (
            TypeError,
            ValueError,
        ) as error:
            selection_failures += 1
            failed_morphemes += 1

            raw_reading = morpheme.reading_form()
            reading_text = (
                raw_reading
                if isinstance(
                    raw_reading,
                    str,
                )
                else repr(raw_reading)
            )

            error_message = str(error)

            key = (
                surface,
                reading_text,
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

        if reading is None:
            continue

        if not should_audit_japanese_part(
            surface,
            reading,
        ):
            continue

        parts.append(
            (
                surface,
                reading,
                part_of_speech_name,
            )
        )

    total_morphemes = (
        len(parts)
        + selection_failures
    )

    index = 0

    while index < len(parts):
        (
            surface,
            reading,
            part_of_speech_name,
        ) = parts[index]

        if (
            reading.endswith("ッ")
            and index + 1 < len(parts)
        ):
            next_reading = parts[
                index + 1
            ][1]

            try:
                romanizer(
                    reading + next_reading
                )
            except ValueError:
                pass
            else:
                successful_morphemes += 2
                index += 2
                continue

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

            index += 1
            continue

        successful_morphemes += 1
        index += 1

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



SUDACHI_TEXT_MAX_BYTES = 48_000


def split_sudachi_text_chunks(
    text: str,
    *,
    max_bytes: int = SUDACHI_TEXT_MAX_BYTES,
) -> tuple[str, ...]:
    if max_bytes <= 0:
        raise ValueError(
            "max_bytes must be greater than 0"
        )

    if not text:
        return ()

    if len(
        text.encode("utf-8")
    ) <= max_bytes:
        return (text,)

    lines = text.splitlines(
        keepends=True
    )

    chunks: list[str] = []
    current_lines: list[str] = []
    current_bytes = 0

    for line in lines:
        line_bytes = len(
            line.encode("utf-8")
        )

        if line_bytes > max_bytes:
            raise ValueError(
                "Single line exceeds Sudachi byte limit"
            )

        if (
            current_lines
            and current_bytes + line_bytes
            > max_bytes
        ):
            chunks.append(
                "".join(current_lines)
            )
            current_lines = []
            current_bytes = 0

        current_lines.append(line)
        current_bytes += line_bytes

    if current_lines:
        chunks.append(
            "".join(current_lines)
        )

    return tuple(chunks)



def audit_japanese_text(
    text: str,
    *,
    tokenizer: SudachiTokenizer,
    romanizer: Callable[[str], str],
) -> JapaneseAuditResult:
    chunks = split_sudachi_text_chunks(
        text
    )

    return merge_japanese_audit_results(
        audit_japanese_morphemes(
            tokenizer.tokenize(
                normalize_fullwidth_ascii(
                    normalize_text(chunk)
                )
            ),
            romanizer=romanizer,
            context=text,
        )
        for chunk in chunks
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
