from __future__ import annotations

from collections.abc import Iterable

from .corpus_build_result import CorpusBuildResult
from .text_normalizer import (
    normalize_fullwidth_ascii,
    normalize_text,
)


def build_english_corpus(
    documents: Iterable[str],
) -> CorpusBuildResult:
    document_list = tuple(documents)

    if not document_list:
        raise ValueError(
            "documents must not be empty"
        )

    processed_documents: list[str] = []

    for document in document_list:
        if not document:
            raise ValueError(
                "document must not be empty"
            )

        processed_documents.append(
            normalize_fullwidth_ascii(
                normalize_text(document)
            )
        )

    return CorpusBuildResult(
        category="english",
        text=" ".join(
            processed_documents
        ),
        source_document_count=len(
            document_list
        ),
    )
