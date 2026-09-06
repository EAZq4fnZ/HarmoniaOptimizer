from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .corpus_build_result import CorpusBuildResult


def write_corpus_build_artifact(
    *,
    result: CorpusBuildResult,
    text_path: Path,
    manifest_path: Path,
    source_snapshot_sha256: str,
    sampling_seed: int,
) -> None:
    text_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    manifest_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_bytes = result.text.encode(
        "utf-8"
    )

    text_path.write_bytes(
        output_bytes
    )

    output_sha256 = hashlib.sha256(
        output_bytes
    ).hexdigest()

    manifest = {
        "schema_version": "1.0",
        "category": result.category,
        "source_document_count": (
            result.source_document_count
        ),
        "processed_characters": len(
            result.text
        ),
        "ascii_letter_count": (
            result.ascii_letter_count
        ),
        "source_snapshot_sha256": (
            source_snapshot_sha256
        ),
        "sampling_seed": sampling_seed,
        "output_sha256": output_sha256,
    }

    manifest_path.write_text(
        json.dumps(
            manifest,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
