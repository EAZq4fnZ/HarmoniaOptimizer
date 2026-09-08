from corpus_builder.document_sampler import sample_documents_streaming
from corpus_builder.huggingface_rows_source import (
    generate_sample_indices,
    generate_sample_ranges,
    iter_sampled_row_blocks,
)


def test_generate_sample_indices_returns_requested_count() -> None:
    result = generate_sample_indices(
        population_size=1000,
        sample_size=25,
        seed=12345,
    )

    assert len(result) == 25


def test_generate_sample_indices_contains_unique_indices() -> None:
    result = generate_sample_indices(
        population_size=1000,
        sample_size=25,
        seed=12345,
    )

    assert len(set(result)) == 25


def test_generate_sample_indices_stays_inside_population() -> None:
    result = generate_sample_indices(
        population_size=1000,
        sample_size=25,
        seed=12345,
    )

    assert all(
        0 <= index < 1000
        for index in result
    )


def test_generate_sample_indices_is_deterministic() -> None:
    first = generate_sample_indices(
        population_size=1000,
        sample_size=25,
        seed=12345,
    )

    second = generate_sample_indices(
        population_size=1000,
        sample_size=25,
        seed=12345,
    )

    assert first == second


def test_generate_sample_indices_rejects_non_positive_population_size() -> None:
    try:
        generate_sample_indices(
            population_size=0,
            sample_size=0,
            seed=12345,
        )
    except ValueError as error:
        assert str(error) == (
            "population_size must be greater than 0"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


def test_generate_sample_indices_rejects_negative_sample_size() -> None:
    try:
        generate_sample_indices(
            population_size=100,
            sample_size=-1,
            seed=12345,
        )
    except ValueError as error:
        assert str(error) == (
            "sample_size must be greater than or equal to 0"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


def test_generate_sample_indices_rejects_sample_larger_than_population() -> None:
    try:
        generate_sample_indices(
            population_size=10,
            sample_size=11,
            seed=12345,
        )
    except ValueError as error:
        assert str(error) == (
            "sample_size must not exceed population_size"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


from corpus_builder.huggingface_rows_source import (
    build_row_ranges,
)


def test_build_row_ranges_groups_contiguous_indices() -> None:
    result = build_row_ranges(
        (
            1,
            2,
            3,
            20,
            21,
            105,
        )
    )

    assert result == (
        (1, 3),
        (20, 2),
        (105, 1),
    )


def test_build_row_ranges_sorts_indices() -> None:
    result = build_row_ranges(
        (
            21,
            3,
            20,
            1,
            105,
            2,
        )
    )

    assert result == (
        (1, 3),
        (20, 2),
        (105, 1),
    )


def test_build_row_ranges_returns_empty_for_no_indices() -> None:
    result = build_row_ranges(
        ()
    )

    assert result == ()


def test_build_row_ranges_splits_ranges_at_max_length() -> None:
    result = build_row_ranges(
        tuple(
            range(205)
        ),
        max_length=100,
    )

    assert result == (
        (0, 100),
        (100, 100),
        (200, 5),
    )


def test_build_row_ranges_rejects_non_positive_max_length() -> None:
    try:
        build_row_ranges(
            (
                1,
                2,
                3,
            ),
            max_length=0,
        )
    except ValueError as error:
        assert str(error) == (
            "max_length must be greater than 0"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


def test_build_row_ranges_removes_duplicate_indices() -> None:
    result = build_row_ranges(
        (
            1,
            2,
            2,
            3,
            20,
            20,
            21,
        )
    )

    assert result == (
        (1, 3),
        (20, 2),
    )


def test_build_row_ranges_rejects_negative_index() -> None:
    try:
        build_row_ranges(
            (
                1,
                -1,
                2,
            )
        )
    except ValueError as error:
        assert str(error) == (
            "indices must not contain negative values"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


from corpus_builder.huggingface_rows_source import (
    build_rows_url,
)


def test_build_rows_url_builds_dataset_viewer_request() -> None:
    result = build_rows_url(
        dataset="singletongue/cc100-documents",
        config="ja",
        split="train",
        offset=150,
        length=25,
    )

    assert result == (
        "https://datasets-server.huggingface.co/rows"
        "?dataset=singletongue%2Fcc100-documents"
        "&config=ja"
        "&split=train"
        "&offset=150"
        "&length=25"
    )


def test_build_rows_url_encodes_query_parameters() -> None:
    result = build_rows_url(
        dataset="owner/dataset name",
        config="日本語",
        split="train test",
        offset=0,
        length=1,
    )

    assert result == (
        "https://datasets-server.huggingface.co/rows"
        "?dataset=owner%2Fdataset+name"
        "&config=%E6%97%A5%E6%9C%AC%E8%AA%9E"
        "&split=train+test"
        "&offset=0"
        "&length=1"
    )


def test_build_rows_url_rejects_negative_offset() -> None:
    try:
        build_rows_url(
            dataset="singletongue/cc100-documents",
            config="ja",
            split="train",
            offset=-1,
            length=1,
        )
    except ValueError as error:
        assert str(error) == (
            "offset must be greater than or equal to 0"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


def test_build_rows_url_rejects_non_positive_length() -> None:
    try:
        build_rows_url(
            dataset="singletongue/cc100-documents",
            config="ja",
            split="train",
            offset=0,
            length=0,
        )
    except ValueError as error:
        assert str(error) == (
            "length must be greater than 0"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


def test_build_rows_url_rejects_length_above_100() -> None:
    try:
        build_rows_url(
            dataset="singletongue/cc100-documents",
            config="ja",
            split="train",
            offset=0,
            length=101,
        )
    except ValueError as error:
        assert str(error) == (
            "length must not exceed 100"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


from corpus_builder.huggingface_rows_source import (
    parse_rows_response,
)


def test_parse_rows_response_extracts_text_values() -> None:
    payload = {
        "rows": [
            {
                "row": {
                    "idx": 1,
                    "start_ln": 10,
                    "text": "alpha",
                }
            },
            {
                "row": {
                    "idx": 2,
                    "start_ln": 20,
                    "text": "bravo",
                }
            },
        ]
    }

    result = parse_rows_response(
        payload,
        text_field="text",
    )

    assert result == (
        "alpha",
        "bravo",
    )


def test_parse_rows_response_supports_custom_text_field() -> None:
    payload = {
        "rows": [
            {
                "row": {
                    "content": "alpha",
                }
            },
        ]
    }

    result = parse_rows_response(
        payload,
        text_field="content",
    )

    assert result == (
        "alpha",
    )


def test_parse_rows_response_rejects_missing_rows() -> None:
    try:
        parse_rows_response(
            {},
            text_field="text",
        )
    except ValueError as error:
        assert str(error) == (
            "Missing 'rows' in response"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


def test_parse_rows_response_rejects_non_list_rows() -> None:
    try:
        parse_rows_response(
            {
                "rows": {},
            },
            text_field="text",
        )
    except TypeError as error:
        assert str(error) == (
            "'rows' must be a list"
        )
    else:
        raise AssertionError(
            "TypeError was not raised"
        )


def test_parse_rows_response_rejects_missing_text_field() -> None:
    payload = {
        "rows": [
            {
                "row": {
                    "idx": 1,
                }
            },
        ]
    }

    try:
        parse_rows_response(
            payload,
            text_field="text",
        )
    except ValueError as error:
        assert str(error) == (
            "Missing text field 'text' in response row"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


def test_parse_rows_response_rejects_non_string_text() -> None:
    payload = {
        "rows": [
            {
                "row": {
                    "text": 123,
                }
            },
        ]
    }

    try:
        parse_rows_response(
            payload,
            text_field="text",
        )
    except TypeError as error:
        assert str(error) == (
            "Text field 'text' must be a string"
        )
    else:
        raise AssertionError(
            "TypeError was not raised"
        )


from typing import Self

from corpus_builder.huggingface_rows_source import (
    fetch_rows,
)


class FakeResponse:
    def __init__(
        self,
        body: str,
    ) -> None:
        self._body = body

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: object,
        exc_value: object,
        traceback: object,
    ) -> None:
        return None

    def read(self) -> bytes:
        return self._body.encode(
            "utf-8"
        )


def test_fetch_rows_fetches_and_parses_documents() -> None:
    requested_urls: list[str] = []

    def fake_open(
        url: str,
            *,
            timeout: float,
    ) -> FakeResponse:
        requested_urls.append(
            url
        )

        return FakeResponse(
            """
            {
              "rows": [
                {
                  "row": {
                    "text": "alpha"
                  }
                },
                {
                  "row": {
                    "text": "bravo"
                  }
                }
              ]
            }
            """
        )

    result = fetch_rows(
        dataset="singletongue/cc100-documents",
        config="ja",
        split="train",
        offset=150,
        length=2,
        text_field="text",
        opener=fake_open,
    )

    assert result == (
        "alpha",
        "bravo",
    )

    assert requested_urls == [
        (
            "https://datasets-server.huggingface.co/rows"
            "?dataset=singletongue%2Fcc100-documents"
            "&config=ja"
            "&split=train"
            "&offset=150"
            "&length=2"
        )
    ]


def test_fetch_rows_rejects_invalid_json() -> None:
    def fake_open(
        url: str,
            *,
            timeout: float,
    ) -> FakeResponse:
        return FakeResponse(
            "not json"
        )

    try:
        fetch_rows(
            dataset="singletongue/cc100-documents",
            config="ja",
            split="train",
            offset=0,
            length=1,
            text_field="text",
            opener=fake_open,
        )
    except ValueError as error:
        assert str(error) == (
            "Invalid JSON response"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


from corpus_builder.huggingface_rows_source import (
    iter_sampled_rows,
)


def test_iter_sampled_rows_fetches_selected_documents() -> None:
    requests: list[
        tuple[int, int]
    ] = []

    documents_by_offset = {
        0: ("alpha",),
        4: ("echo",),
        6: ("golf",),
    }

    def fake_fetch(
        *,
        dataset: str,
        config: str,
        split: str,
        offset: int,
        length: int,
        text_field: str,
    ) -> tuple[str, ...]:
        requests.append(
            (
                offset,
                length,
            )
        )

        return documents_by_offset[
            offset
        ]

    result = tuple(
        iter_sampled_rows(
            dataset="example/dataset",
            config="ja",
            split="train",
            population_size=10,
            sample_size=3,
            seed=12345,
            text_field="text",
            fetcher=fake_fetch,
        )
    )

    expected_indices = generate_sample_indices(
        population_size=10,
        sample_size=3,
        seed=12345,
    )

    expected_ranges = build_row_ranges(
        expected_indices
    )

    assert requests == list(
        expected_ranges
    )

    assert len(result) == 3


def test_iter_sampled_rows_rejects_unexpected_document_count() -> None:
    def fake_fetch(
        *,
        dataset: str,
        config: str,
        split: str,
        offset: int,
        length: int,
        text_field: str,
    ) -> tuple[str, ...]:
        return ()

    try:
        tuple(
            iter_sampled_rows(
                dataset="example/dataset",
                config="ja",
                split="train",
                population_size=10,
                sample_size=3,
                seed=12345,
                text_field="text",
                fetcher=fake_fetch,
            )
        )
    except ValueError as error:
        assert str(error) == (
            "Fetched document count does not match requested length"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


import itertools
from urllib.error import HTTPError, URLError


def test_fetch_rows_wraps_http_error() -> None:
    def fake_open(
        url: str,
            *,
            timeout: float,
    ) -> FakeResponse:
        raise HTTPError(
            url,
            503,
            "Service Unavailable",
            hdrs=None,
            fp=None,
        )

    try:
        fetch_rows(
            dataset="singletongue/cc100-documents",
            config="ja",
            split="train",
            offset=0,
            length=1,
            text_field="text",
            opener=fake_open,
        )
    except RuntimeError as error:
        assert str(error) == (
            "Failed to fetch rows"
        )
    else:
        raise AssertionError(
            "RuntimeError was not raised"
        )


def test_fetch_rows_wraps_url_error() -> None:
    def fake_open(
        url: str,
            *,
            timeout: float,
    ) -> FakeResponse:
        raise URLError(
            "connection failed"
        )

    try:
        fetch_rows(
            dataset="singletongue/cc100-documents",
            config="ja",
            split="train",
            offset=0,
            length=1,
            text_field="text",
            opener=fake_open,
        )
    except RuntimeError as error:
        assert str(error) == (
            "Failed to fetch rows"
        )
    else:
        raise AssertionError(
            "RuntimeError was not raised"
        )


def test_fetch_rows_passes_timeout_to_opener() -> None:
    calls: list[
        tuple[str, float]
    ] = []

    def fake_open(
        url: str,
        *,
        timeout: float,
    ) -> FakeResponse:
        calls.append(
            (
                url,
                timeout,
            )
        )

        return FakeResponse(
            """
            {
              "rows": [
                {
                  "row": {
                    "text": "alpha"
                  }
                }
              ]
            }
            """
        )

    result = fetch_rows(
        dataset="singletongue/cc100-documents",
        config="ja",
        split="train",
        offset=0,
        length=1,
        text_field="text",
        timeout=15.0,
        opener=fake_open,
    )

    assert result == (
        "alpha",
    )

    assert calls[0][1] == 15.0


def test_fetch_rows_rejects_non_positive_timeout() -> None:
    try:
        fetch_rows(
            dataset="singletongue/cc100-documents",
            config="ja",
            split="train",
            offset=0,
            length=1,
            text_field="text",
            timeout=0,
        )
    except ValueError as error:
        assert str(error) == (
            "timeout must be greater than 0"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


def test_generate_sample_ranges_returns_requested_document_count() -> None:
    ranges = generate_sample_ranges(
        population_size=1_000,
        document_count=250,
        seed=12345,
        block_size=100,
    )

    assert sum(
        length
        for _, length in ranges
    ) == 250


def test_generate_sample_ranges_respects_block_size() -> None:
    ranges = generate_sample_ranges(
        population_size=1_000,
        document_count=250,
        seed=12345,
        block_size=100,
    )

    assert all(
        1 <= length <= 100
        for _, length in ranges
    )


def test_generate_sample_ranges_stays_within_population() -> None:
    ranges = generate_sample_ranges(
        population_size=1_000,
        document_count=250,
        seed=12345,
        block_size=100,
    )

    assert all(
        0 <= offset
        and offset + length <= 1_000
        for offset, length in ranges
    )


def test_generate_sample_ranges_is_deterministic() -> None:
    first = generate_sample_ranges(
        population_size=1_000,
        document_count=250,
        seed=12345,
        block_size=100,
    )

    second = generate_sample_ranges(
        population_size=1_000,
        document_count=250,
        seed=12345,
        block_size=100,
    )

    assert first == second


def test_generate_sample_ranges_do_not_overlap() -> None:
    ranges = generate_sample_ranges(
        population_size=1_000,
        document_count=250,
        seed=12345,
        block_size=100,
    )

    ordered = sorted(
        ranges
    )

    assert all(
        offset + length <= next_offset
        for (
            offset,
            length,
        ), (
            next_offset,
            _,
        ) in itertools.pairwise(ordered)
    )


def test_generate_sample_ranges_handles_partial_final_block() -> None:
    ranges = generate_sample_ranges(
        population_size=1_000,
        document_count=250,
        seed=12345,
        block_size=100,
    )

    lengths = sorted(
        length
        for _, length in ranges
    )

    assert lengths == [
        50,
        100,
        100,
    ]


def test_generate_sample_ranges_rejects_non_positive_population_size() -> None:
    try:
        generate_sample_ranges(
            population_size=0,
            document_count=1,
            seed=12345,
            block_size=100,
        )
    except ValueError as error:
        assert str(error) == (
            "population_size must be greater than 0"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


def test_generate_sample_ranges_rejects_negative_document_count() -> None:
    try:
        generate_sample_ranges(
            population_size=1_000,
            document_count=-1,
            seed=12345,
            block_size=100,
        )
    except ValueError as error:
        assert str(error) == (
            "document_count must be greater than or equal to 0"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


def test_generate_sample_ranges_rejects_document_count_above_population() -> None:
    try:
        generate_sample_ranges(
            population_size=100,
            document_count=101,
            seed=12345,
            block_size=100,
        )
    except ValueError as error:
        assert str(error) == (
            "document_count must not exceed population_size"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


def test_generate_sample_ranges_rejects_non_positive_block_size() -> None:
    try:
        generate_sample_ranges(
            population_size=1_000,
            document_count=10,
            seed=12345,
            block_size=0,
        )
    except ValueError as error:
        assert str(error) == (
            "block_size must be greater than 0"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


def test_iter_sampled_row_blocks_fetches_generated_ranges() -> None:
    requests: list[
        tuple[int, int]
    ] = []

    def fake_fetch(
        *,
        dataset: str,
        config: str,
        split: str,
        offset: int,
        length: int,
        text_field: str,
        **kwargs: object,
    ) -> tuple[str, ...]:
        requests.append(
            (
                offset,
                length,
            )
        )

        return tuple(
            f"document-{offset + index}"
            for index in range(
                length
            )
        )

    result = tuple(
        iter_sampled_row_blocks(
            dataset="singletongue/cc100-documents",
            config="ja",
            split="train",
            population_size=1_000,
            document_count=250,
            seed=12345,
            text_field="text",
            block_size=100,
            fetcher=fake_fetch,
        )
    )

    expected_ranges = generate_sample_ranges(
        population_size=1_000,
        document_count=250,
        seed=12345,
        block_size=100,
    )

    assert requests == list(
        expected_ranges
    )

    assert len(result) == 250


def test_iter_sampled_row_blocks_rejects_unexpected_document_count() -> None:
    def fake_fetch(
        *,
        dataset: str,
        config: str,
        split: str,
        offset: int,
        length: int,
        text_field: str,
        **kwargs: object,
    ) -> tuple[str, ...]:
        return ()

    try:
        tuple(
            iter_sampled_row_blocks(
                dataset="singletongue/cc100-documents",
                config="ja",
                split="train",
                population_size=1_000,
                document_count=250,
                seed=12345,
                text_field="text",
                block_size=100,
                fetcher=fake_fetch,
            )
        )
    except ValueError as error:
        assert str(error) == (
            "Fetched document count does not match requested length"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )


def test_iter_sampled_row_blocks_uses_minimum_request_count() -> None:
    requests: list[
        tuple[int, int]
    ] = []

    def fake_fetch(
        *,
        dataset: str,
        config: str,
        split: str,
        offset: int,
        length: int,
        text_field: str,
        **kwargs: object,
    ) -> tuple[str, ...]:
        requests.append(
            (
                offset,
                length,
            )
        )

        return tuple(
            "document"
            for _ in range(
                length
            )
        )

    tuple(
        iter_sampled_row_blocks(
            dataset="singletongue/cc100-documents",
            config="ja",
            split="train",
            population_size=1_000,
            document_count=250,
            seed=12345,
            text_field="text",
            block_size=100,
            fetcher=fake_fetch,
        )
    )

    assert len(
        requests
    ) == 3


def test_sampled_row_blocks_feed_streaming_sampler() -> None:
    source_documents = (
        "alpha" * 30,
        "bravo" * 30,
        "charlie" * 30,
        "delta" * 30,
        "echo" * 30,
        "alpha" * 30,
        "short",
    )

    def fake_fetch(
        *,
        dataset: str,
        config: str,
        split: str,
        offset: int,
        length: int,
        text_field: str,
        **kwargs: object,
    ) -> tuple[str, ...]:
        start = offset

        return tuple(
            source_documents[
                start:start + length
            ]
        )

    documents = iter_sampled_row_blocks(
        dataset="example/dataset",
        config="ja",
        split="train",
        population_size=len(
            source_documents
        ),
        document_count=len(
            source_documents
        ),
        seed=12345,
        text_field="text",
        block_size=3,
        fetcher=fake_fetch,
    )

    sampled = sample_documents_streaming(
        documents,
        sample_size=3,
        seed=67890,
        min_length=100,
    )

    assert len(sampled) == 3

    assert len(
        set(sampled)
    ) == 3

    assert all(
        len(document) >= 100
        for document in sampled
    )

def test_fetch_rows_retries_http_429() -> None:
    attempts = 0
    sleep_calls: list[float] = []

    def fake_open(
        url: str,
        *,
        timeout: float,
    ) -> FakeResponse:
        nonlocal attempts

        attempts += 1

        if attempts == 1:
            raise HTTPError(
                url,
                429,
                "Too Many Requests",
                hdrs=None,
                fp=None,
            )

        return FakeResponse(
            """
            {
              "rows": [
                {
                  "row": {
                    "text": "alpha"
                  }
                }
              ]
            }
            """
        )

    result = fetch_rows(
        dataset="singletongue/cc100-documents",
        config="en",
        split="train",
        offset=0,
        length=1,
        text_field="text",
        opener=fake_open,
        sleeper=sleep_calls.append,
    )

    assert result == (
        "alpha",
    )
    assert attempts == 2
    assert sleep_calls == [
        1.0,
    ]

def test_fetch_rows_retries_repeated_http_429_with_exponential_backoff() -> None:
    attempts = 0
    sleep_calls: list[float] = []

    def fake_open(
        url: str,
        *,
        timeout: float,
    ) -> FakeResponse:
        nonlocal attempts

        attempts += 1

        if attempts <= 3:
            raise HTTPError(
                url,
                429,
                "Too Many Requests",
                hdrs=None,
                fp=None,
            )

        return FakeResponse(
            """
            {
              "rows": [
                {
                  "row": {
                    "text": "alpha"
                  }
                }
              ]
            }
            """
        )

    result = fetch_rows(
        dataset="singletongue/cc100-documents",
        config="en",
        split="train",
        offset=0,
        length=1,
        text_field="text",
        opener=fake_open,
        sleeper=sleep_calls.append,
    )

    assert result == (
        "alpha",
    )
    assert attempts == 4
    assert sleep_calls == [
        1.0,
        2.0,
        4.0,
    ]


def test_fetch_rows_stops_retrying_http_429_after_limit() -> None:
    attempts = 0
    sleep_calls: list[float] = []

    def fake_open(
        url: str,
        *,
        timeout: float,
    ) -> FakeResponse:
        nonlocal attempts

        attempts += 1

        raise HTTPError(
            url,
            429,
            "Too Many Requests",
            hdrs=None,
            fp=None,
        )

    try:
        fetch_rows(
            dataset="singletongue/cc100-documents",
            config="en",
            split="train",
            offset=0,
            length=1,
            text_field="text",
            opener=fake_open,
            sleeper=sleep_calls.append,
        )
    except RuntimeError as error:
        assert str(error) == (
            "Failed to fetch rows"
        )
    else:
        raise AssertionError(
            "RuntimeError was not raised"
        )

    assert attempts == 5
    assert sleep_calls == [
        1.0,
        2.0,
        4.0,
        8.0,
    ]

def test_iter_sampled_row_blocks_waits_between_requests() -> None:
    requests: list[
        tuple[int, int]
    ] = []
    sleep_calls: list[float] = []

    def fake_fetch(
        *,
        dataset: str,
        config: str,
        split: str,
        offset: int,
        length: int,
        text_field: str,
        **kwargs: object,
    ) -> tuple[str, ...]:
        requests.append(
            (
                offset,
                length,
            )
        )

        return tuple(
            "document"
            for _ in range(
                length
            )
        )

    result = tuple(
        iter_sampled_row_blocks(
            dataset="example/dataset",
            config="en",
            split="train",
            population_size=1_000,
            document_count=250,
            seed=12345,
            text_field="text",
            block_size=100,
            request_delay=3.0,
            sleeper=sleep_calls.append,
            fetcher=fake_fetch,
        )
    )

    assert len(
        requests
    ) == 3

    assert len(
        result
    ) == 250

    assert sleep_calls == [
        3.0,
        3.0,
    ]

def test_iter_sampled_row_blocks_rejects_negative_request_delay() -> None:
    try:
        tuple(
            iter_sampled_row_blocks(
                dataset="example/dataset",
                config="en",
                split="train",
                population_size=10,
                document_count=1,
                seed=12345,
                text_field="text",
                request_delay=-1.0,
            )
        )
    except ValueError as error:
        assert str(error) == (
            "request_delay must be greater than or equal to 0"
        )
    else:
        raise AssertionError(
            "ValueError was not raised"
        )

def test_fetch_rows_retries_http_502() -> None:
    attempts = 0
    sleep_calls: list[float] = []

    def fake_open(
        url: str,
        *,
        timeout: float,
    ) -> FakeResponse:
        nonlocal attempts

        attempts += 1

        if attempts == 1:
            raise HTTPError(
                url,
                502,
                "Bad Gateway",
                hdrs=None,
                fp=None,
            )

        return FakeResponse(
            """
            {
              "rows": [
                {
                  "row": {
                    "text": "alpha"
                  }
                }
              ]
            }
            """
        )

    result = fetch_rows(
        dataset="singletongue/cc100-documents",
        config="en",
        split="train",
        offset=0,
        length=1,
        text_field="text",
        opener=fake_open,
        sleeper=sleep_calls.append,
    )

    assert result == (
        "alpha",
    )
    assert attempts == 2
    assert sleep_calls == [
        1.0,
    ]
