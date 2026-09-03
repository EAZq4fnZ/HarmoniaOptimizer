from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path


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
