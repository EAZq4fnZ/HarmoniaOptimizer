from __future__ import annotations

import json
import random
from collections.abc import Callable, Iterator
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen


def generate_sample_indices(
    *,
    population_size: int,
    sample_size: int,
    seed: int,
) -> tuple[int, ...]:
    if population_size <= 0:
        raise ValueError(
            "population_size must be greater than 0"
        )

    if sample_size < 0:
        raise ValueError(
            "sample_size must be greater than or equal to 0"
        )

    if sample_size > population_size:
        raise ValueError(
            "sample_size must not exceed population_size"
        )

    return tuple(
        random.Random(seed).sample(
            range(population_size),
            sample_size,
        )
    )



def generate_sample_ranges(
    *,
    population_size: int,
    document_count: int,
    seed: int,
    block_size: int = 100,
) -> tuple[tuple[int, int], ...]:
    if population_size <= 0:
        raise ValueError(
            "population_size must be greater than 0"
        )

    if document_count < 0:
        raise ValueError(
            "document_count must be greater than or equal to 0"
        )

    if document_count > population_size:
        raise ValueError(
            "document_count must not exceed population_size"
        )

    if block_size <= 0:
        raise ValueError(
            "block_size must be greater than 0"
        )

    if document_count == 0:
        return ()

    full_block_count, remainder = divmod(
        document_count,
        block_size,
    )

    lengths = [
        block_size
        for _ in range(
            full_block_count
        )
    ]

    if remainder:
        lengths.append(
            remainder
        )

    randomizer = random.Random(
        seed
    )

    randomizer.shuffle(
        lengths
    )

    slack = (
        population_size
        - document_count
    )

    separator_count = len(
        lengths
    )

    separators = sorted(
        randomizer.sample(
            range(
                slack
                + separator_count
            ),
            separator_count,
        )
    )

    gaps: list[int] = []
    previous = -1

    for separator in separators:
        gaps.append(
            separator
            - previous
            - 1
        )
        previous = separator

    gaps.append(
        slack
        + separator_count
        - previous
        - 1
    )

    ranges: list[
        tuple[int, int]
    ] = []

    offset = gaps[0]

    for index, length in enumerate(
        lengths
    ):
        ranges.append(
            (
                offset,
                length,
            )
        )

        offset += (
            length
            + gaps[index + 1]
        )

    return tuple(
        ranges
    )


def build_row_ranges(
    indices: tuple[int, ...],
    *,
    max_length: int = 100,
) -> tuple[tuple[int, int], ...]:
    if max_length <= 0:
        raise ValueError(
            "max_length must be greater than 0"
        )

    if not indices:
        return ()

    if any(
        index < 0
        for index in indices
    ):
        raise ValueError(
            "indices must not contain negative values"
        )

    sorted_indices = sorted(
        set(indices)
    )

    ranges: list[tuple[int, int]] = []

    start = sorted_indices[0]
    previous = start
    length = 1

    for index in sorted_indices[1:]:
        is_contiguous = (
            index == previous + 1
        )
        has_capacity = (
            length < max_length
        )

        if is_contiguous and has_capacity:
            length += 1
        else:
            ranges.append(
                (
                    start,
                    length,
                )
            )
            start = index
            length = 1

        previous = index

    ranges.append(
        (
            start,
            length,
        )
    )

    return tuple(
        ranges
    )



def build_rows_url(
    *,
    dataset: str,
    config: str,
    split: str,
    offset: int,
    length: int,
) -> str:
    if offset < 0:
        raise ValueError(
            "offset must be greater than or equal to 0"
        )

    if length <= 0:
        raise ValueError(
            "length must be greater than 0"
        )

    if length > 100:
        raise ValueError(
            "length must not exceed 100"
        )

    query = urlencode(
        {
            "dataset": dataset,
            "config": config,
            "split": split,
            "offset": offset,
            "length": length,
        }
    )

    return (
        "https://datasets-server.huggingface.co/rows"
        f"?{query}"
    )



def parse_rows_response(
    payload: object,
    *,
    text_field: str,
) -> tuple[str, ...]:
    if not isinstance(
        payload,
        dict,
    ):
        raise TypeError(
            "response payload must be an object"
        )

    if "rows" not in payload:
        raise ValueError(
            "Missing 'rows' in response"
        )

    rows = payload["rows"]

    if not isinstance(
        rows,
        list,
    ):
        raise TypeError(
            "'rows' must be a list"
        )

    documents: list[str] = []

    for item in rows:
        if not isinstance(
            item,
            dict,
        ):
            raise TypeError(
                "Response row entry must be an object"
            )

        row = item.get(
            "row"
        )

        if not isinstance(
            row,
            dict,
        ):
            raise TypeError(
                "'row' must be an object"
            )

        if text_field not in row:
            raise ValueError(
                f"Missing text field '{text_field}' "
                "in response row"
            )

        document = row[text_field]

        if not isinstance(
            document,
            str,
        ):
            raise TypeError(
                f"Text field '{text_field}' "
                "must be a string"
            )

        documents.append(
            document
        )

    return tuple(
        documents
    )



def fetch_rows(
    *,
    dataset: str,
    config: str,
    split: str,
    offset: int,
    length: int,
    text_field: str,
    timeout: float = 30.0,
    opener: Callable[..., object] = urlopen,
    sleeper: Callable[[float], None] | None = None,
) -> tuple[str, ...]:
    if timeout <= 0:
        raise ValueError(
            "timeout must be greater than 0"
        )

    url = build_rows_url(
        dataset=dataset,
        config=config,
        split=split,
        offset=offset,
        length=length,
    )

    max_attempts = 5

    for attempt in range(max_attempts):
        try:
            with opener(
                url,
                timeout=timeout,
            ) as response:
                body = response.read()
            break
        except HTTPError as error:
            is_retryable = (
                error.code == 429
                and attempt
                < max_attempts - 1
            )

            if is_retryable:
                delay = float(
                    2 ** attempt
                )

                if sleeper is None:
                    from time import sleep

                    sleep(delay)
                else:
                    sleeper(delay)

                continue

            raise RuntimeError(
                "Failed to fetch rows"
            ) from error
        except URLError as error:
            raise RuntimeError(
                "Failed to fetch rows"
            ) from error

    try:
        payload = json.loads(
            body.decode(
                "utf-8"
            )
        )
    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as error:
        raise ValueError(
            "Invalid JSON response"
        ) from error

    return parse_rows_response(
        payload,
        text_field=text_field,
    )

def iter_sampled_row_blocks(
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
) -> Iterator[str]:
    if request_delay < 0:
        raise ValueError(
            "request_delay must be greater than or equal to 0"
        )

    ranges = generate_sample_ranges(
        population_size=population_size,
        document_count=document_count,
        seed=seed,
        block_size=block_size,
    )

    for range_index, (
        offset,
        length,
    ) in enumerate(ranges):
        documents = fetcher(
            dataset=dataset,
            config=config,
            split=split,
            offset=offset,
            length=length,
            text_field=text_field,
        )

        if len(documents) != length:
            raise ValueError(
                "Fetched document count does not match requested length"
            )

        yield from documents

        should_wait = (
            request_delay > 0
            and range_index
            < len(ranges) - 1
        )

        if should_wait:
            if sleeper is None:
                from time import sleep

                sleep(
                    request_delay
                )
            else:
                sleeper(
                    request_delay
                )

def iter_sampled_rows(
    *,
    dataset: str,
    config: str,
    split: str,
    population_size: int,
    sample_size: int,
    seed: int,
    text_field: str,
    fetcher: Callable[..., tuple[str, ...]] = fetch_rows,
) -> Iterator[str]:
    indices = generate_sample_indices(
        population_size=population_size,
        sample_size=sample_size,
        seed=seed,
    )

    ranges = build_row_ranges(
        indices
    )

    for offset, length in ranges:
        documents = fetcher(
            dataset=dataset,
            config=config,
            split=split,
            offset=offset,
            length=length,
            text_field=text_field,
        )

        if len(documents) != length:
            raise ValueError(
                "Fetched document count does not match requested length"
            )

        yield from documents
