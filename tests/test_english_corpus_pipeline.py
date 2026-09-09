import json
from pathlib import Path

from corpus_builder.english_corpus_pipeline import (
    build_sampled_english_corpus,
    write_sampled_english_corpus_artifact,
)
from corpus_builder.source_snapshot import (
    hash_document_snapshot,
)


def test_build_sampled_english_corpus_builds_result_from_sampled_rows() -> None:
    calls: list[
        tuple[
            str,
            str,
            str,
            int,
            int,
            str,
        ]
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
        calls.append(
            (
                dataset,
                config,
                split,
                offset,
                length,
                text_field,
            )
        )

        return tuple(
            f"Document {offset + index}."
            for index in range(length)
        )

    result = build_sampled_english_corpus(
        dataset="example/dataset",
        config="default",
        split="train",
        population_size=1000,
        document_count=5,
        seed=42,
        text_field="text",
        block_size=3,
        fetcher=fake_fetcher,
    )

    assert result.category == "english"
    assert result.source_document_count == 5
    assert result.ascii_letter_count > 0
    assert result.text

    assert sum(
        call[4]
        for call in calls
    ) == 5


def test_build_sampled_english_corpus_is_reproducible_for_same_seed() -> None:
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
            f"Document {offset + index}."
            for index in range(length)
        )

    first = build_sampled_english_corpus(
        dataset="example/dataset",
        config="default",
        split="train",
        population_size=1000,
        document_count=25,
        seed=42,
        text_field="text",
        fetcher=fake_fetcher,
    )

    second = build_sampled_english_corpus(
        dataset="example/dataset",
        config="default",
        split="train",
        population_size=1000,
        document_count=25,
        seed=42,
        text_field="text",
        fetcher=fake_fetcher,
    )

    assert first == second


def test_build_sampled_english_corpus_forwards_request_delay() -> None:
    sleeps: list[float] = []

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
            f"Document {offset + index}."
            for index in range(length)
        )

    result = build_sampled_english_corpus(
        dataset="example/dataset",
        config="default",
        split="train",
        population_size=1000,
        document_count=5,
        seed=42,
        text_field="text",
        block_size=2,
        request_delay=0.25,
        sleeper=sleeps.append,
        fetcher=fake_fetcher,
    )

    assert result.source_document_count == 5
    assert sleeps == [
        0.25,
        0.25,
    ]


def test_write_sampled_english_corpus_artifact_writes_result_and_manifest(
    tmp_path: Path,
) -> None:
    raw_documents: list[str] = []

    def fake_fetcher(
        *,
        dataset: str,
        config: str,
        split: str,
        offset: int,
        length: int,
        text_field: str,
    ) -> tuple[str, ...]:
        documents = tuple(
            f" Ｄｏｃｕｍｅｎｔ {offset + index}. "
            for index in range(length)
        )

        raw_documents.extend(
            documents
        )

        return documents

    text_path = (
        tmp_path
        / "english.txt"
    )
    manifest_path = (
        tmp_path
        / "english.manifest.json"
    )

    result = (
        write_sampled_english_corpus_artifact(
            dataset="example/dataset",
            config="default",
            split="train",
            population_size=1000,
            document_count=5,
            seed=42,
            text_field="text",
            text_path=text_path,
            manifest_path=manifest_path,
            block_size=3,
            fetcher=fake_fetcher,
        )
    )

    assert result.category == "english"
    assert result.source_document_count == 5

    assert text_path.read_text(
        encoding="utf-8"
    ) == result.text

    manifest = json.loads(
        manifest_path.read_text(
            encoding="utf-8"
        )
    )

    assert manifest[
        "category"
    ] == "english"

    assert manifest[
        "source_document_count"
    ] == 5

    assert manifest[
        "sampling_seed"
    ] == 42

    assert manifest[
        "source_snapshot_sha256"
    ] == hash_document_snapshot(
        raw_documents
    )

    assert manifest[
        "processed_characters"
    ] == len(
        result.text
    )

    assert manifest[
        "ascii_letter_count"
    ] == result.ascii_letter_count
