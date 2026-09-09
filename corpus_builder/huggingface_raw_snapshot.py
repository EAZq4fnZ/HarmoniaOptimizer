from __future__ import annotations

import hashlib
import json
import tempfile
import time
from collections.abc import Callable
from pathlib import Path

from .huggingface_rows_source import (
    fetch_rows,
    generate_sample_ranges,
)

SAMPLING_METHOD = (
    "deterministic_non_overlapping_blocks"
)


def _create_temporary_path(
    target_path: Path,
) -> Path:
    with tempfile.NamedTemporaryFile(
        prefix=f".{target_path.name}.",
        suffix=".tmp",
        dir=target_path.parent,
        delete=False,
    ) as temporary_file:
        return Path(
            temporary_file.name
        )


def write_huggingface_raw_snapshot(
    *,
    dataset: str,
    config: str,
    split: str,
    population_size: int,
    document_count: int,
    seed: int,
    text_field: str,
    snapshot_path: Path,
    manifest_path: Path,
    block_size: int = 100,
    request_delay: float = 0.0,
    sleeper: Callable[[float], None] | None = None,
    fetcher: Callable[..., tuple[str, ...]] = fetch_rows,
) -> str:
    if request_delay < 0:
        raise ValueError(
            "request_delay must not be negative"
        )

    if sleeper is None:
        sleeper = time.sleep

    ranges = generate_sample_ranges(
        population_size=population_size,
        document_count=document_count,
        seed=seed,
        block_size=block_size,
    )

    snapshot_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    manifest_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_snapshot_path = (
        _create_temporary_path(
            snapshot_path
        )
    )

    digest = hashlib.sha256()
    written_documents = 0

    try:
        with temporary_snapshot_path.open(
            "wb"
        ) as snapshot_file:
            for range_index, (
                offset,
                length,
            ) in enumerate(ranges):
                documents = fetcher(
                    dataset=dataset,
                    config=config,
                    split=split,
                    offset=offset,
                    length=length,
                    text_field=text_field,
                )

                if len(documents) != length:
                    raise RuntimeError(
                        "Fetched document count "
                        "does not match requested "
                        "range length"
                    )

                for (
                    document_index,
                    document,
                ) in enumerate(documents):
                    row_idx = (
                        offset
                        + document_index
                    )

                    record = {
                        "row_idx": row_idx,
                        "text": document,
                    }

                    record_bytes = (
                        json.dumps(
                            record,
                            ensure_ascii=False,
                        )
                        + "\n"
                    ).encode(
                        "utf-8"
                    )

                    snapshot_file.write(
                        record_bytes
                    )
                    digest.update(
                        record_bytes
                    )

                    written_documents += 1

                if (
                    request_delay > 0
                    and range_index
                    < len(ranges) - 1
                ):
                    sleeper(
                        request_delay
                    )

        if (
            written_documents
            != document_count
        ):
            raise RuntimeError(
                "Written document count "
                "does not match requested "
                "document_count"
            )

        snapshot_sha256 = (
            digest.hexdigest()
        )

        manifest = {
            "schema_version": "1.0",
            "source": {
                "provider": "huggingface",
                "dataset": dataset,
                "config": config,
                "split": split,
                "population_size": (
                    population_size
                ),
            },
            "sampling": {
                "method": (
                    SAMPLING_METHOD
                ),
                "document_count": (
                    document_count
                ),
                "seed": seed,
                "block_size": (
                    block_size
                ),
                "ranges": [
                    {
                        "offset": offset,
                        "length": length,
                    }
                    for offset, length
                    in ranges
                ],
            },
            "snapshot": {
                "path": (
                    snapshot_path.as_posix()
                ),
                "document_count": (
                    written_documents
                ),
                "sha256": (
                    snapshot_sha256
                ),
            },
        }

        manifest_bytes = (
            json.dumps(
                manifest,
                ensure_ascii=False,
                indent=2,
            )
            + "\n"
        ).encode(
            "utf-8"
        )

        temporary_manifest_path = (
            _create_temporary_path(
                manifest_path
            )
        )

        try:
            temporary_manifest_path.write_bytes(
                manifest_bytes
            )

            temporary_snapshot_path.replace(
                snapshot_path
            )

            temporary_manifest_path.replace(
                manifest_path
            )
        finally:
            temporary_manifest_path.unlink(
                missing_ok=True
            )

        return snapshot_sha256

    finally:
        temporary_snapshot_path.unlink(
            missing_ok=True
        )

