from __future__ import annotations

from collections.abc import Callable, Iterable

from .corpus_build_result import CorpusBuildResult
from .japanese_corpus_part import JapaneseCorpusPart
from .japanese_preprocessor import (
    preprocess_japanese_source,
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
    canonicalizer: Callable[[str], str] | None = None,
) -> CorpusBuildResult:
    document_list = tuple(documents)

    if not document_list:
        raise ValueError(
            "documents must not be empty"
        )

    use_structured_preprocessing = (
        part_reader is not None
        or canonicalizer is not None
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

        if use_structured_preprocessing:
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

        processed_documents.append(
            processed
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
