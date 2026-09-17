from __future__ import annotations

from collections.abc import Callable, Iterable

from .corpus_build_result import CorpusBuildResult
from .japanese_corpus_occurrence import (
    JapaneseCorpusOccurrence,
)
from .japanese_corpus_part import JapaneseCorpusPart
from .japanese_preprocessor import (
    preprocess_japanese_source,
    preprocess_occurrence_aware_japanese_source,
    preprocess_structured_japanese_source,
)


def build_japanese_corpus(
    documents: Iterable[str],
    *,
    reader: Callable[[str], str] | None = None,
    romanizer: Callable[[str], str] | None = None,
    part_reader: Callable[
        [str],
        Iterable[JapaneseCorpusPart],
    ]
    | None = None,
    occurrence_reader: Callable[
        [str],
        Iterable[JapaneseCorpusOccurrence],
    ]
    | None = None,
    canonicalizer: Callable[[str], str] | None = None,
) -> CorpusBuildResult:
    document_list = tuple(documents)

    if not document_list:
        raise ValueError(
            "documents must not be empty"
        )

    if (
        part_reader is not None
        and occurrence_reader is not None
    ):
        raise ValueError(
            "part_reader and occurrence_reader "
            "must not be used together"
        )

    use_occurrence_preprocessing = (
        occurrence_reader is not None
    )
    use_structured_preprocessing = (
        not use_occurrence_preprocessing
        and (
            part_reader is not None
            or canonicalizer is not None
        )
    )

    if use_occurrence_preprocessing:
        if romanizer is None:
            raise ValueError(
                "romanizer is required for "
                "occurrence-aware Japanese preprocessing"
            )

        if canonicalizer is None:
            raise ValueError(
                "canonicalizer is required for "
                "occurrence-aware Japanese preprocessing"
            )

    if use_structured_preprocessing:
        if part_reader is None:
            raise ValueError(
                "part_reader is required for "
                "structured Japanese preprocessing"
            )

        if romanizer is None:
            raise ValueError(
                "romanizer is required for "
                "structured Japanese preprocessing"
            )

        if canonicalizer is None:
            raise ValueError(
                "canonicalizer is required for "
                "structured Japanese preprocessing"
            )

    processed_documents: list[str] = []

    for document in document_list:
        if not document:
            raise ValueError(
                "document must not be empty"
            )

        if use_occurrence_preprocessing:
            assert occurrence_reader is not None
            assert romanizer is not None
            assert canonicalizer is not None

            processed = (
                preprocess_occurrence_aware_japanese_source(
                    document,
                    occurrence_reader=occurrence_reader,
                    romanizer=romanizer,
                    canonicalizer=canonicalizer,
                )
            )
        elif use_structured_preprocessing:
            assert part_reader is not None
            assert romanizer is not None
            assert canonicalizer is not None

            processed = (
                preprocess_structured_japanese_source(
                    document,
                    part_reader=part_reader,
                    romanizer=romanizer,
                    canonicalizer=canonicalizer,
                )
            )
        else:
            processed = preprocess_japanese_source(
                document,
                reader=reader,
                romanizer=romanizer,
            )

        if processed is not None:
            processed_documents.append(
                processed
            )

    if not processed_documents:
        raise ValueError(
            "Japanese corpus preprocessing "
            "excluded all documents"
        )

    return CorpusBuildResult(
        category="japanese",
        text=" ".join(
            processed_documents
        ),
        source_document_count=len(
            document_list
        ),
    )
