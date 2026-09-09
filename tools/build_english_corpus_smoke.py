from __future__ import annotations

import json
from pathlib import Path

from corpus_builder.english_corpus_pipeline import (
    write_snapshotted_english_corpus_artifacts,
)

DATASET = "singletongue/cc100-documents"
CONFIG = "en"
SPLIT = "train"
POPULATION_SIZE = 247_588_106
DOCUMENT_COUNT = 100
SEED = 20260910
TEXT_FIELD = "text"
BLOCK_SIZE = 100
REQUEST_DELAY = 0.25

BASE_NAME = (
    "cc100-en-seed-20260910-smoke-100"
)

RAW_SNAPSHOT_PATH = Path(
    "corpus/raw/cc100-en"
) / f"{BASE_NAME}.jsonl"

RAW_MANIFEST_PATH = Path(
    "corpus/manifests/cc100-en"
) / f"{BASE_NAME}.raw.manifest.json"

PROCESSED_TEXT_PATH = Path(
    "corpus/processed/english"
) / f"{BASE_NAME}.txt"

PROCESSED_MANIFEST_PATH = Path(
    "corpus/manifests/cc100-en"
) / f"{BASE_NAME}.processed.manifest.json"


def main() -> None:
    result = (
        write_snapshotted_english_corpus_artifacts(
            dataset=DATASET,
            config=CONFIG,
            split=SPLIT,
            population_size=POPULATION_SIZE,
            document_count=DOCUMENT_COUNT,
            seed=SEED,
            text_field=TEXT_FIELD,
            raw_snapshot_path=(
                RAW_SNAPSHOT_PATH
            ),
            raw_manifest_path=(
                RAW_MANIFEST_PATH
            ),
            processed_text_path=(
                PROCESSED_TEXT_PATH
            ),
            processed_manifest_path=(
                PROCESSED_MANIFEST_PATH
            ),
            block_size=BLOCK_SIZE,
            request_delay=REQUEST_DELAY,
        )
    )

    raw_manifest = json.loads(
        RAW_MANIFEST_PATH.read_text(
            encoding="utf-8"
        )
    )

    processed_manifest = json.loads(
        PROCESSED_MANIFEST_PATH.read_text(
            encoding="utf-8"
        )
    )

    print(
        "category:",
        result.category,
    )
    print(
        "source_document_count:",
        result.source_document_count,
    )
    print(
        "processed_characters:",
        len(result.text),
    )
    print(
        "ascii_letter_count:",
        result.ascii_letter_count,
    )

    print(
        "raw_snapshot_sha256:",
        raw_manifest[
            "snapshot"
        ][
            "sha256"
        ],
    )

    print(
        "source_snapshot_sha256:",
        processed_manifest[
            "source_snapshot_sha256"
        ],
    )

    print(
        "output_sha256:",
        processed_manifest[
            "output_sha256"
        ],
    )

    print(
        "raw_snapshot_path:",
        RAW_SNAPSHOT_PATH,
    )
    print(
        "raw_manifest_path:",
        RAW_MANIFEST_PATH,
    )
    print(
        "processed_text_path:",
        PROCESSED_TEXT_PATH,
    )
    print(
        "processed_manifest_path:",
        PROCESSED_MANIFEST_PATH,
    )


if __name__ == "__main__":
    main()
