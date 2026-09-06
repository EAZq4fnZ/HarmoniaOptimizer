from __future__ import annotations

from collections.abc import Callable, Iterable

from .corpus_build_result import CorpusBuildResult
from .japanese_preprocessor import preprocess_japanese_source


def build_japanese_corpus(
    documents: Iterable[str],
    *,
    reader: Callable[[str], str] | None = None,
    romanizer: Callable[[str], str] | None = None,
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
            preprocess_japanese_source(
                document,
                reader=reader,
                romanizer=romanizer,
            )
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
