from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from corpus_builder.document_sampler import (
    sample_documents_streaming,
)
from corpus_builder.document_source import (
    iter_jsonl_documents,
    iter_parquet_documents,
)


def test_iter_jsonl_documents_reads_text_field(
    tmp_path: Path,
) -> None:
    source = tmp_path / "documents.jsonl"
    source.write_text(
        '{"text": "alpha"}\n{"text": "bravo"}\n{"text": "charlie"}',
        encoding="utf-8",
    )

    result = tuple(
        iter_jsonl_documents(
            source,
            text_field="text",
        )
    )

    assert result == (
        "alpha",
        "bravo",
        "charlie",
    )


def test_iter_jsonl_documents_supports_custom_text_field(
    tmp_path: Path,
) -> None:
    source = tmp_path / "documents.jsonl"
    source.write_text(
        '{"content": "alpha"}\n{"content": "bravo"}',
        encoding="utf-8",
    )

    result = tuple(
        iter_jsonl_documents(
            source,
            text_field="content",
        )
    )

    assert result == (
        "alpha",
        "bravo",
    )


def test_iter_jsonl_documents_skips_blank_lines(
    tmp_path: Path,
) -> None:
    source = tmp_path / "documents.jsonl"
    source.write_text(
        '{"text": "alpha"}\n\n   \n{"text": "bravo"}',
        encoding="utf-8",
    )

    result = tuple(
        iter_jsonl_documents(
            source,
            text_field="text",
        )
    )

    assert result == (
        "alpha",
        "bravo",
    )


def test_iter_jsonl_documents_reports_invalid_json_line_number(
    tmp_path: Path,
) -> None:
    source = tmp_path / "documents.jsonl"
    source.write_text(
        '{"text": "alpha"}\n{invalid json}\n{"text": "bravo"}',
        encoding="utf-8",
    )

    try:
        tuple(
            iter_jsonl_documents(
                source,
                text_field="text",
            )
        )
    except ValueError as error:
        assert str(error) == (
            "Invalid JSON on line 2"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


def test_iter_jsonl_documents_reports_missing_text_field(
    tmp_path: Path,
) -> None:
    source = tmp_path / "documents.jsonl"
    source.write_text(
        '{"text": "alpha"}\n{"content": "bravo"}',
        encoding="utf-8",
    )

    try:
        tuple(
            iter_jsonl_documents(
                source,
                text_field="text",
            )
        )
    except ValueError as error:
        assert str(error) == (
            "Missing text field 'text' on line 2"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


def test_iter_jsonl_documents_rejects_non_string_text_field(
    tmp_path: Path,
) -> None:
    source = tmp_path / "documents.jsonl"
    source.write_text(
        '{"text": "alpha"}\n{"text": 123}',
        encoding="utf-8",
    )

    try:
        tuple(
            iter_jsonl_documents(
                source,
                text_field="text",
            )
        )
    except TypeError as error:
        assert str(error) == (
            "Text field 'text' must be a string "
            "on line 2"
        )
    else:
        raise AssertionError(
            "TypeError was not raised"
        )


def test_iter_jsonl_documents_rejects_non_object_record(
    tmp_path: Path,
) -> None:
    source = tmp_path / "documents.jsonl"
    source.write_text(
        '{"text": "alpha"}\n["bravo"]',
        encoding="utf-8",
    )

    try:
        tuple(
            iter_jsonl_documents(
                source,
                text_field="text",
            )
        )
    except TypeError as error:
        assert str(error) == (
            "JSONL record must be an object "
            "on line 2"
        )
    else:
        raise AssertionError(
            "TypeError was not raised"
        )


def test_jsonl_documents_can_feed_streaming_sampler(
    tmp_path: Path,
) -> None:
    source = tmp_path / "documents.jsonl"
    source.write_text(
        '{"text": "alpha"}\n{"text": "bravo"}\n{"text": "charlie"}\n{"text": "delta"}\n{"text": "echo"}',
        encoding="utf-8",
    )

    documents = iter_jsonl_documents(
        source,
        text_field="text",
    )

    result = sample_documents_streaming(
        documents,
        sample_size=3,
        seed=12345,
    )

    assert len(result) == 3
    assert len(set(result)) == 3
    assert set(result) <= {
        "alpha",
        "bravo",
        "charlie",
        "delta",
        "echo",
    }


def test_jsonl_streaming_sample_is_deterministic(
    tmp_path: Path,
) -> None:
    source = tmp_path / "documents.jsonl"
    source.write_text(
        '{"text": "alpha"}\n{"text": "bravo"}\n{"text": "charlie"}\n{"text": "delta"}\n{"text": "echo"}',
        encoding="utf-8",
    )

    first = sample_documents_streaming(
        iter_jsonl_documents(
            source,
            text_field="text",
        ),
        sample_size=3,
        seed=12345,
    )

    second = sample_documents_streaming(
        iter_jsonl_documents(
            source,
            text_field="text",
        ),
        sample_size=3,
        seed=12345,
    )

    assert first == second


def test_iter_parquet_documents_reads_text_field(
    tmp_path: Path,
) -> None:
    source = tmp_path / "documents.parquet"

    table = pa.table(
        {
            "text": (
                "alpha",
                "bravo",
                "charlie",
            )
        }
    )

    pq.write_table(
        table,
        source,
    )

    result = tuple(
        iter_parquet_documents(
            source,
            text_field="text",
        )
    )

    assert result == (
        "alpha",
        "bravo",
        "charlie",
    )


def test_iter_parquet_documents_supports_custom_text_field(
    tmp_path: Path,
) -> None:
    source = tmp_path / "documents.parquet"

    table = pa.table(
        {
            "content": (
                "alpha",
                "bravo",
            )
        }
    )

    pq.write_table(
        table,
        source,
    )

    result = tuple(
        iter_parquet_documents(
            source,
            text_field="content",
        )
    )

    assert result == (
        "alpha",
        "bravo",
    )


def test_iter_parquet_documents_reports_missing_text_field(
    tmp_path: Path,
) -> None:
    source = tmp_path / "documents.parquet"

    table = pa.table(
        {
            "content": (
                "alpha",
                "bravo",
            )
        }
    )

    pq.write_table(
        table,
        source,
    )

    try:
        tuple(
            iter_parquet_documents(
                source,
                text_field="text",
            )
        )
    except ValueError as error:
        assert str(error) == (
            "Missing text field 'text' "
            "in Parquet schema"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


def test_iter_parquet_documents_rejects_non_string_text_field(
    tmp_path: Path,
) -> None:
    source = tmp_path / "documents.parquet"

    table = pa.table(
        {
            "text": (
                123,
                456,
            )
        }
    )

    pq.write_table(
        table,
        source,
    )

    try:
        tuple(
            iter_parquet_documents(
                source,
                text_field="text",
            )
        )
    except TypeError as error:
        assert str(error) == (
            "Text field 'text' must be a string column "
            "in Parquet schema"
        )
    else:
        raise AssertionError(
            "TypeError was not raised"
        )


def test_iter_parquet_documents_rejects_null_text_value(
    tmp_path: Path,
) -> None:
    source = tmp_path / "documents.parquet"

    table = pa.table(
        {
            "text": (
                "alpha",
                None,
                "bravo",
            )
        }
    )

    pq.write_table(
        table,
        source,
    )

    try:
        tuple(
            iter_parquet_documents(
                source,
                text_field="text",
            )
        )
    except TypeError as error:
        assert str(error) == (
            "Text field 'text' must not contain null values"
        )
    else:
        raise AssertionError(
            "TypeError was not raised"
        )


def test_iter_parquet_documents_accepts_batch_size(
    tmp_path: Path,
) -> None:
    source = tmp_path / "documents.parquet"

    table = pa.table(
        {
            "text": (
                "alpha",
                "bravo",
                "charlie",
                "delta",
            )
        }
    )

    pq.write_table(
        table,
        source,
    )

    result = tuple(
        iter_parquet_documents(
            source,
            text_field="text",
            batch_size=2,
        )
    )

    assert result == (
        "alpha",
        "bravo",
        "charlie",
        "delta",
    )


def test_iter_parquet_documents_rejects_zero_batch_size(
    tmp_path: Path,
) -> None:
    source = tmp_path / "documents.parquet"

    table = pa.table(
        {
            "text": (
                "alpha",
                "bravo",
            )
        }
    )

    pq.write_table(
        table,
        source,
    )

    try:
        tuple(
            iter_parquet_documents(
                source,
                text_field="text",
                batch_size=0,
            )
        )
    except ValueError as error:
        assert str(error) == (
            "batch_size must be greater than 0"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


def test_iter_parquet_documents_rejects_negative_batch_size(
    tmp_path: Path,
) -> None:
    source = tmp_path / "documents.parquet"

    table = pa.table(
        {
            "text": (
                "alpha",
                "bravo",
            )
        }
    )

    pq.write_table(
        table,
        source,
    )

    try:
        tuple(
            iter_parquet_documents(
                source,
                text_field="text",
                batch_size=-1,
            )
        )
    except ValueError as error:
        assert str(error) == (
            "batch_size must be greater than 0"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


def test_parquet_documents_can_feed_streaming_sampler(
    tmp_path: Path,
) -> None:
    source = tmp_path / "documents.parquet"

    table = pa.table(
        {
            "text": (
                "alpha",
                "bravo",
                "charlie",
                "delta",
                "echo",
            )
        }
    )

    pq.write_table(
        table,
        source,
    )

    documents = iter_parquet_documents(
        source,
        text_field="text",
        batch_size=2,
    )

    result = sample_documents_streaming(
        documents,
        sample_size=3,
        seed=12345,
    )

    assert len(result) == 3
    assert len(set(result)) == 3
    assert set(result) <= {
        "alpha",
        "bravo",
        "charlie",
        "delta",
        "echo",
    }


def test_parquet_streaming_sample_is_deterministic(
    tmp_path: Path,
) -> None:
    source = tmp_path / "documents.parquet"

    table = pa.table(
        {
            "text": (
                "alpha",
                "bravo",
                "charlie",
                "delta",
                "echo",
            )
        }
    )

    pq.write_table(
        table,
        source,
    )

    first = sample_documents_streaming(
        iter_parquet_documents(
            source,
            text_field="text",
            batch_size=2,
        ),
        sample_size=3,
        seed=12345,
    )

    second = sample_documents_streaming(
        iter_parquet_documents(
            source,
            text_field="text",
            batch_size=2,
        ),
        sample_size=3,
        seed=12345,
    )

    assert first == second
