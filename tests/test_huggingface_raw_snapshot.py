from __future__ import annotations

import hashlib
import json
from pathlib import Path

from corpus_builder.huggingface_raw_snapshot import (
    SAMPLING_METHOD,
    write_huggingface_raw_snapshot,
)


def test_write_huggingface_raw_snapshot(
    tmp_path: Path,
) -> None:
    snapshot_path = (
        tmp_path
        / "snapshot.jsonl"
    )

    manifest_path = (
        tmp_path
        / "manifest.json"
    )

    requested_ranges: list[
        tuple[int, int]
    ] = []

    def fake_fetcher(
        *,
        dataset: str,
        config: str,
        split: str,
        offset: int,
        length: int,
        text_field: str,
    ) -> tuple[str, ...]:
        assert dataset == "example/data"
        assert config == "en"
        assert split == "train"
        assert text_field == "text"

        requested_ranges.append(
            (
                offset,
                length,
            )
        )

        return tuple(
            f"document-{row_idx}"
            for row_idx in range(
                offset,
                offset + length,
            )
        )

    sha256 = (
        write_huggingface_raw_snapshot(
            dataset="example/data",
            config="en",
            split="train",
            population_size=100,
            document_count=5,
            seed=123,
            text_field="text",
            snapshot_path=snapshot_path,
            manifest_path=(
                manifest_path
            ),
            block_size=2,
            fetcher=fake_fetcher,
        )
    )

    raw_bytes = (
        snapshot_path.read_bytes()
    )

    assert sha256 == (
        hashlib.sha256(
            raw_bytes
        ).hexdigest()
    )

    records = [
        json.loads(line)
        for line in (
            snapshot_path.read_text(
                encoding="utf-8"
            ).splitlines()
        )
    ]

    assert len(records) == 5

    expected_row_indexes = [
        row_idx
        for offset, length
        in requested_ranges
        for row_idx in range(
            offset,
            offset + length,
        )
    ]

    assert [
        record["row_idx"]
        for record in records
    ] == expected_row_indexes

    assert [
        record["text"]
        for record in records
    ] == [
        f"document-{row_idx}"
        for row_idx
        in expected_row_indexes
    ]

    manifest = json.loads(
        manifest_path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        manifest["schema_version"]
        == "1.0"
    )

    assert manifest["source"] == {
        "provider": "huggingface",
        "dataset": "example/data",
        "config": "en",
        "split": "train",
        "population_size": 100,
    }

    assert (
        manifest["sampling"]["method"]
        == SAMPLING_METHOD
    )

    assert (
        manifest["sampling"][
            "document_count"
        ]
        == 5
    )

    assert (
        manifest["sampling"]["seed"]
        == 123
    )

    assert (
        manifest["sampling"][
            "block_size"
        ]
        == 2
    )

    assert (
        manifest["snapshot"][
            "document_count"
        ]
        == 5
    )

    assert (
        manifest["snapshot"]["sha256"]
        == sha256
    )


def test_write_huggingface_raw_snapshot_is_reproducible(
    tmp_path: Path,
) -> None:
    first_snapshot = (
        tmp_path
        / "first.jsonl"
    )

    first_manifest = (
        tmp_path
        / "first.json"
    )

    second_snapshot = (
        tmp_path
        / "second.jsonl"
    )

    second_manifest = (
        tmp_path
        / "second.json"
    )

    def fake_fetcher(
        *,
        dataset: str,
        config: str,
        split: str,
        offset: int,
        length: int,
        text_field: str,
    ) -> tuple[str, ...]:
        return tuple(
            f"text-{row_idx}"
            for row_idx in range(
                offset,
                offset + length,
            )
        )

    common = {
        "dataset": "example/data",
        "config": "en",
        "split": "train",
        "population_size": 100,
        "document_count": 7,
        "seed": 456,
        "text_field": "text",
        "block_size": 3,
        "fetcher": fake_fetcher,
    }

    first_sha256 = (
        write_huggingface_raw_snapshot(
            snapshot_path=(
                first_snapshot
            ),
            manifest_path=(
                first_manifest
            ),
            **common,
        )
    )

    second_sha256 = (
        write_huggingface_raw_snapshot(
            snapshot_path=(
                second_snapshot
            ),
            manifest_path=(
                second_manifest
            ),
            **common,
        )
    )

    assert (
        first_snapshot.read_bytes()
        == second_snapshot.read_bytes()
    )

    assert (
        first_sha256
        == second_sha256
    )


def test_write_huggingface_raw_snapshot_propagates_delay(
    tmp_path: Path,
) -> None:
    sleep_calls: list[
        float
    ] = []

    def fake_fetcher(
        *,
        dataset: str,
        config: str,
        split: str,
        offset: int,
        length: int,
        text_field: str,
    ) -> tuple[str, ...]:
        return tuple(
            "text"
            for _ in range(length)
        )

    write_huggingface_raw_snapshot(
        dataset="example/data",
        config="en",
        split="train",
        population_size=100,
        document_count=5,
        seed=789,
        text_field="text",
        snapshot_path=(
            tmp_path
            / "snapshot.jsonl"
        ),
        manifest_path=(
            tmp_path
            / "manifest.json"
        ),
        block_size=2,
        request_delay=0.25,
        sleeper=sleep_calls.append,
        fetcher=fake_fetcher,
    )

    assert sleep_calls == [
        0.25,
        0.25,
    ]


def test_write_huggingface_raw_snapshot_rejects_wrong_fetch_count(
    tmp_path: Path,
) -> None:
    def fake_fetcher(
        *,
        dataset: str,
        config: str,
        split: str,
        offset: int,
        length: int,
        text_field: str,
    ) -> tuple[str, ...]:
        return (
            "too-short",
        )

    try:
        write_huggingface_raw_snapshot(
            dataset="example/data",
            config="en",
            split="train",
            population_size=100,
            document_count=5,
            seed=123,
            text_field="text",
            snapshot_path=(
                tmp_path
                / "snapshot.jsonl"
            ),
            manifest_path=(
                tmp_path
                / "manifest.json"
            ),
            block_size=2,
            fetcher=fake_fetcher,
        )
    except RuntimeError as error:
        assert str(error) == (
            "Fetched document count "
            "does not match requested "
            "range length"
        )
    else:
        raise AssertionError(
            "Expected RuntimeError"
        )


def test_write_huggingface_raw_snapshot_rejects_negative_delay(
    tmp_path: Path,
) -> None:
    try:
        write_huggingface_raw_snapshot(
            dataset="example/data",
            config="en",
            split="train",
            population_size=100,
            document_count=5,
            seed=123,
            text_field="text",
            snapshot_path=(
                tmp_path
                / "snapshot.jsonl"
            ),
            manifest_path=(
                tmp_path
                / "manifest.json"
            ),
            request_delay=-0.1,
        )
    except ValueError as error:
        assert str(error) == (
            "request_delay must not be negative"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_write_huggingface_raw_snapshot_preserves_existing_snapshot_on_failure(
    tmp_path: Path,
) -> None:
    snapshot_path = (
        tmp_path
        / "snapshot.jsonl"
    )

    manifest_path = (
        tmp_path
        / "manifest.json"
    )

    original_snapshot = (
        b'{"row_idx": 1, "text": "existing"}\n'
    )

    snapshot_path.write_bytes(
        original_snapshot
    )

    manifest_path.write_text(
        '{"existing": true}\n',
        encoding="utf-8",
    )

    fetch_count = 0

    def failing_fetcher(
        *,
        dataset: str,
        config: str,
        split: str,
        offset: int,
        length: int,
        text_field: str,
    ) -> tuple[str, ...]:
        nonlocal fetch_count

        fetch_count += 1

        if fetch_count == 1:
            return tuple(
                f"text-{row_idx}"
                for row_idx in range(
                    offset,
                    offset + length,
                )
            )

        raise RuntimeError(
            "simulated fetch failure"
        )

    try:
        write_huggingface_raw_snapshot(
            dataset="example/data",
            config="en",
            split="train",
            population_size=100,
            document_count=5,
            seed=123,
            text_field="text",
            snapshot_path=snapshot_path,
            manifest_path=manifest_path,
            block_size=2,
            fetcher=failing_fetcher,
        )
    except RuntimeError as error:
        assert str(error) == (
            "simulated fetch failure"
        )
    else:
        raise AssertionError(
            "Expected RuntimeError"
        )

    assert (
        snapshot_path.read_bytes()
        == original_snapshot
    )

    assert (
        manifest_path.read_text(
            encoding="utf-8"
        )
        == '{"existing": true}\n'
    )
