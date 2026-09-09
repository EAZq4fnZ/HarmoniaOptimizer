from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from .corpus_build_artifact import (
    write_corpus_build_artifact,
)
from .corpus_build_result import CorpusBuildResult
from .english_corpus_builder import build_english_corpus
from .huggingface_rows_source import (
    fetch_rows,
    iter_sampled_row_blocks,
)
from .source_snapshot import hash_document_snapshot


def _sample_english_documents(
    *,
    dataset: str,
    config: str,
    split: str,
    population_size: int,
    document_count: int,
    seed: int,
    text_field: str,
    block_size: int,
    request_delay: float,
    sleeper: Callable[[float], None] | None,
    fetcher: Callable[..., tuple[str, ...]],
) -> tuple[str, ...]:
    return tuple(
        iter_sampled_row_blocks(
            dataset=dataset,
            config=config,
            split=split,
            population_size=population_size,
            document_count=document_count,
            seed=seed,
            text_field=text_field,
            block_size=block_size,
            request_delay=request_delay,
            sleeper=sleeper,
            fetcher=fetcher,
        )
    )


def build_sampled_english_corpus(
    *,
    dataset: str,
    config: str,
    split: str,
    population_size: int,
    document_count: int,
    seed: int,
    text_field: str,
    block_size: int = 100,
    request_delay: float = 0.0,
    sleeper: Callable[[float], None] | None = None,
    fetcher: Callable[..., tuple[str, ...]] = fetch_rows,
) -> CorpusBuildResult:
    documents = _sample_english_documents(
        dataset=dataset,
        config=config,
        split=split,
        population_size=population_size,
        document_count=document_count,
        seed=seed,
        text_field=text_field,
        block_size=block_size,
        request_delay=request_delay,
        sleeper=sleeper,
        fetcher=fetcher,
    )

    return build_english_corpus(
        documents
    )


def write_sampled_english_corpus_artifact(
    *,
    dataset: str,
    config: str,
    split: str,
    population_size: int,
    document_count: int,
    seed: int,
    text_field: str,
    text_path: Path,
    manifest_path: Path,
    block_size: int = 100,
    request_delay: float = 0.0,
    sleeper: Callable[[float], None] | None = None,
    fetcher: Callable[..., tuple[str, ...]] = fetch_rows,
) -> CorpusBuildResult:
    documents = _sample_english_documents(
        dataset=dataset,
        config=config,
        split=split,
        population_size=population_size,
        document_count=document_count,
        seed=seed,
        text_field=text_field,
        block_size=block_size,
        request_delay=request_delay,
        sleeper=sleeper,
        fetcher=fetcher,
    )

    source_snapshot_sha256 = (
        hash_document_snapshot(
            documents
        )
    )

    result = build_english_corpus(
        documents
    )

    write_corpus_build_artifact(
        result=result,
        text_path=text_path,
        manifest_path=manifest_path,
        source_snapshot_sha256=(
            source_snapshot_sha256
        ),
        sampling_seed=seed,
    )

    return result
