from __future__ import annotations

from collections.abc import Iterable
from hashlib import sha256
from heapq import heappush, heapreplace
from random import Random


def sample_documents(
    documents: Iterable[str],
    *,
    sample_size: int,
    seed: int,
    min_length: int | None = None,
) -> tuple[str, ...]:
    if sample_size <= 0:
        raise ValueError(
            "sample_size must be greater than 0"
        )

    if (
        min_length is not None
        and min_length <= 0
    ):
        raise ValueError(
            "min_length must be greater than 0"
        )

    unique_documents = tuple(
        sorted(
            {
                document
                for document in documents
                if document.strip()
                and (
                    min_length is None
                    or len(document) >= min_length
                )
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



def sample_documents_streaming(
    documents: Iterable[str],
    *,
    sample_size: int,
    seed: int,
    min_length: int | None = None,
) -> tuple[str, ...]:
    if sample_size <= 0:
        raise ValueError(
            "sample_size must be greater than 0"
        )

    if (
        min_length is not None
        and min_length <= 0
    ):
        raise ValueError(
            "min_length must be greater than 0"
        )

    selected: list[
        tuple[int, str]
    ] = []
    selected_documents: set[str] = set()

    for document in documents:
        if not document.strip():
            continue

        if (
            min_length is not None
            and len(document) < min_length
        ):
            continue

        if document in selected_documents:
            continue

        digest = sha256()
        digest.update(
            str(seed).encode("utf-8")
        )
        digest.update(b"\0")
        digest.update(
            document.encode("utf-8")
        )

        priority = int.from_bytes(
            digest.digest(),
            byteorder="big",
        )

        item = (
            -priority,
            document,
        )

        if len(selected) < sample_size:
            heappush(
                selected,
                item,
            )
            selected_documents.add(
                document
            )
            continue

        largest_priority = (
            -selected[0][0]
        )

        if priority >= largest_priority:
            continue

        removed = heapreplace(
            selected,
            item,
        )

        selected_documents.remove(
            removed[1]
        )
        selected_documents.add(
            document
        )

    ordered = sorted(
        (
            -negative_priority,
            document,
        )
        for (
            negative_priority,
            document,
        ) in selected
    )

    return tuple(
        document
        for _, document in ordered
    )
