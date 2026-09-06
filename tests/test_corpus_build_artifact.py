from __future__ import annotations

import json
from pathlib import Path

from corpus_builder.corpus_build_artifact import (
    write_corpus_build_artifact,
)
from corpus_builder.corpus_build_result import (
    CorpusBuildResult,
)


def test_write_corpus_build_artifact_writes_text_and_manifest(
    tmp_path: Path,
) -> None:
    result = CorpusBuildResult(
        category="japanese",
        text="abc def",
        source_document_count=2,
    )

    text_path = tmp_path / "japanese.txt"
    manifest_path = tmp_path / "japanese.manifest.json"

    write_corpus_build_artifact(
        result=result,
        text_path=text_path,
        manifest_path=manifest_path,
        source_snapshot_sha256="source-sha",
        sampling_seed=123,
    )

    assert text_path.read_text(
        encoding="utf-8"
    ) == "abc def"

    manifest = json.loads(
        manifest_path.read_text(
            encoding="utf-8"
        )
    )

    assert manifest["schema_version"] == "1.0"
    assert manifest["category"] == "japanese"
    assert manifest["source_document_count"] == 2
    assert manifest["processed_characters"] == 7
    assert manifest["ascii_letter_count"] == 6
    assert manifest["source_snapshot_sha256"] == "source-sha"
    assert manifest["sampling_seed"] == 123
    assert manifest["output_sha256"]


def test_write_corpus_build_artifact_records_exact_output_sha256(
    tmp_path: Path,
) -> None:
    result = CorpusBuildResult(
        category="japanese",
        text="abc",
        source_document_count=1,
    )

    manifest_path = tmp_path / "japanese.manifest.json"

    write_corpus_build_artifact(
        result=result,
        text_path=tmp_path / "japanese.txt",
        manifest_path=manifest_path,
        source_snapshot_sha256="source-sha",
        sampling_seed=123,
    )

    manifest = json.loads(
        manifest_path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        manifest["output_sha256"]
        == "ba7816bf8f01cfea414140de5dae2223"
        "b00361a396177a9cb410ff61f20015ad"
    )
