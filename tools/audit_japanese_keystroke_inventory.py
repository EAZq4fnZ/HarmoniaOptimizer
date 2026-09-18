# tools/audit_japanese_keystroke_inventory.py

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from corpus_builder.document_sampler import (
    sample_documents_streaming,
)
from corpus_builder.japanese_keystroke_inventory import (
    JapaneseKeystrokeInventoryResult,
    JapaneseKeystrokeInventoryRow,
    audit_japanese_keystroke_inventory,
)
from corpus_builder.japanese_reader import (
    make_default_japanese_reader,
)


def iter_jsonl_documents(
    path: Path,
    *,
    text_field: str = "text",
) -> Iterable[str]:
    with path.open(
        "r",
        encoding="utf-8",
    ) as source:
        for line in source:
            row: Any = json.loads(line)

            if not isinstance(row, dict):
                continue

            text = row.get(text_field)

            if isinstance(text, str):
                yield text


def inventory_row_sort_key(
    row: JapaneseKeystrokeInventoryRow,
) -> tuple[
    str,
    str,
    str,
    str,
    str,
]:
    return (
        row.source_text,
        row.processing_text,
        row.ambiguity_class.value,
        row.relation.value,
        row.evidence.value,
    )


def make_inventory_payload(
    result: JapaneseKeystrokeInventoryResult,
) -> dict[str, Any]:
    return {
        "document_count": result.document_count,
        "total_occurrences": result.total_occurrences,
        "ambiguous_occurrences": (
            result.ambiguous_occurrences
        ),
        "rows": [
            {
                "source_text": row.source_text,
                "processing_text": (
                    row.processing_text
                ),
                "ambiguity_class": (
                    row.ambiguity_class.value
                ),
                "relation": row.relation.value,
                "evidence": row.evidence.value,
                "occurrence_count": (
                    row.occurrence_count
                ),
                "document_count": (
                    row.document_count
                ),
            }
            for row in sorted(
                result.rows,
                key=inventory_row_sort_key,
            )
        ],
    }


def audit_sampled_jsonl(
    path: Path,
    *,
    sample_size: int,
    seed: int,
    min_length: int | None,
    text_field: str = "text",
) -> JapaneseKeystrokeInventoryResult:
    documents = sample_documents_streaming(
        iter_jsonl_documents(
            path,
            text_field=text_field,
        ),
        sample_size=sample_size,
        seed=seed,
        min_length=min_length,
    )

    reader = make_default_japanese_reader()

    return audit_japanese_keystroke_inventory(
        documents,
        occurrence_reader=reader.read_occurrences,
    )


def main(
    argv: list[str] | None = None,
) -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "source",
        type=Path,
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        required=True,
    )
    parser.add_argument(
        "--seed",
        type=int,
        required=True,
    )
    parser.add_argument(
        "--min-length",
        type=int,
    )
    parser.add_argument(
        "--text-field",
        default="text",
    )
    parser.add_argument(
        "--output",
        type=Path,
    )

    args = parser.parse_args(argv)

    result = audit_sampled_jsonl(
        args.source,
        sample_size=args.sample_size,
        seed=args.seed,
        min_length=args.min_length,
        text_field=args.text_field,
    )

    print(
        f"document_count: "
        f"{result.document_count}"
    )
    print(
        f"total_occurrences: "
        f"{result.total_occurrences}"
    )
    print(
        f"ambiguous_occurrences: "
        f"{result.ambiguous_occurrences}"
    )
    print(
        f"inventory_rows: "
        f"{len(result.rows)}"
    )

    if args.output is not None:
        payload = make_inventory_payload(
            result
        )

        args.output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        args.output.write_text(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
