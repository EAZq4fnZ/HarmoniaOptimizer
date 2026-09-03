from __future__ import annotations

from collections.abc import Iterable
from random import Random


def sample_documents(
    documents: Iterable[str],
    *,
    sample_size: int,
    seed: int,
) -> tuple[str, ...]:
    if sample_size <= 0:
        raise ValueError(
            "sample_size must be greater than 0"
        )

    unique_documents = tuple(
        sorted(
            {
                document
                for document in documents
                if document.strip()
            }
        )
    )

    shuffled = list(
        unique_documents
    )

    Random(seed).shuffle(
        shuffled
    )

    return tuple(
        shuffled[:sample_size]
    )
