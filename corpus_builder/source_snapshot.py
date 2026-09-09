from __future__ import annotations

from collections.abc import Iterable
from hashlib import sha256

_SNAPSHOT_DOMAIN = (
    b"harmonia-corpus-source-snapshot-v1\0"
)


def hash_document_snapshot(
    documents: Iterable[str],
) -> str:
    digest = sha256()
    digest.update(
        _SNAPSHOT_DOMAIN
    )

    document_count = 0

    for document in documents:
        if not isinstance(
            document,
            str,
        ):
            raise TypeError(
                "document must be a string"
            )

        encoded_document = (
            document.encode(
                "utf-8"
            )
        )

        digest.update(
            len(
                encoded_document
            ).to_bytes(
                8,
                byteorder="big",
            )
        )
        digest.update(
            encoded_document
        )

        document_count += 1

    if document_count == 0:
        raise ValueError(
            "documents must not be empty"
        )

    return digest.hexdigest()
