from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

import pyarrow.parquet as pq
import pyarrow.types as pat


def iter_jsonl_documents(
    path: Path,
    *,
    text_field: str,
) -> Iterator[str]:
    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line_number, line in enumerate(
            file,
            start=1,
        ):
            if not line.strip():
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Invalid JSON on line {line_number}"
                ) from error

            if not isinstance(
                record,
                dict,
            ):
                raise TypeError(
                    "JSONL record must be an object "
                    f"on line {line_number}"
                )

            try:
                document = record[text_field]
            except KeyError as error:
                raise ValueError(
                    f"Missing text field '{text_field}' "
                    f"on line {line_number}"
                ) from error

            if not isinstance(
                document,
                str,
            ):
                raise TypeError(
                    f"Text field '{text_field}' must be a string "
                    f"on line {line_number}"
                )

            yield document



def iter_parquet_documents(
    path: Path,
    *,
    text_field: str,
    batch_size: int = 65536,
) -> Iterator[str]:
    if batch_size <= 0:
        raise ValueError(
            "batch_size must be greater than 0"
        )

    parquet_file = pq.ParquetFile(
        path
    )

    if text_field not in parquet_file.schema_arrow.names:
        raise ValueError(
            f"Missing text field '{text_field}' "
            "in Parquet schema"
        )

    text_type = parquet_file.schema_arrow.field(
        text_field
    ).type

    if not pat.is_string(
        text_type
    ):
        raise TypeError(
            f"Text field '{text_field}' must be a string column "
            "in Parquet schema"
        )

    for batch in parquet_file.iter_batches(
        batch_size=batch_size,
        columns=[text_field],
    ):
        for document in batch.column(0).to_pylist():
            if document is None:
                raise TypeError(
                    f"Text field '{text_field}' "
                    "must not contain null values"
                )

            yield document
