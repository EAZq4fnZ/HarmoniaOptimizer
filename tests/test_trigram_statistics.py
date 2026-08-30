import pytest

from evaluator.trigram_statistics import TrigramStatistics


def test_record_single_trigram() -> None:
    statistics = TrigramStatistics()

    statistics.record(
        "t",
        "h",
        "e",
    )

    assert statistics.raw_count(
        "T",
        "H",
        "E",
    ) == 1

    assert statistics.weighted_count(
        "T",
        "H",
        "E",
    ) == pytest.approx(1.0)


def test_record_normalizes_case() -> None:
    statistics = TrigramStatistics()

    statistics.record(
        "t",
        "H",
        "e",
    )
    statistics.record(
        "T",
        "h",
        "E",
    )

    assert statistics.raw_count(
        "T",
        "H",
        "E",
    ) == 2

    assert statistics.weighted_count(
        "T",
        "H",
        "E",
    ) == pytest.approx(2.0)


def test_record_accumulates_weight() -> None:
    statistics = TrigramStatistics()

    statistics.record(
        "a",
        "b",
        "c",
        weight=0.5,
    )
    statistics.record(
        "a",
        "b",
        "c",
        weight=2.0,
    )

    assert statistics.raw_count(
        "A",
        "B",
        "C",
    ) == 2

    assert statistics.weighted_count(
        "A",
        "B",
        "C",
    ) == pytest.approx(2.5)


def test_total_counts() -> None:
    statistics = TrigramStatistics()

    statistics.record(
        "a",
        "b",
        "c",
        weight=0.5,
    )
    statistics.record(
        "b",
        "c",
        "d",
        weight=2.0,
    )
    statistics.record(
        "a",
        "b",
        "c",
        weight=1.5,
    )

    assert statistics.total_raw_count == 3
    assert statistics.total_weighted_count == pytest.approx(
        4.0
    )


def test_len_returns_unique_trigram_count() -> None:
    statistics = TrigramStatistics()

    statistics.record(
        "a",
        "b",
        "c",
    )
    statistics.record(
        "a",
        "b",
        "c",
    )
    statistics.record(
        "b",
        "c",
        "d",
    )

    assert len(statistics) == 2


def test_evaluation_records_are_deterministic() -> None:
    statistics = TrigramStatistics()

    statistics.record(
        "b",
        "c",
        "d",
        weight=2.0,
    )
    statistics.record(
        "a",
        "b",
        "c",
        weight=0.5,
    )
    statistics.record(
        "a",
        "b",
        "c",
        weight=1.5,
    )

    assert tuple(
        statistics.evaluation_records()
    ) == (
        (
            "A",
            "B",
            "C",
            2,
            pytest.approx(2.0),
        ),
        (
            "B",
            "C",
            "D",
            1,
            pytest.approx(2.0),
        ),
    )


def test_unknown_trigram_returns_zero() -> None:
    statistics = TrigramStatistics()

    assert statistics.raw_count(
        "X",
        "Y",
        "Z",
    ) == 0

    assert statistics.weighted_count(
        "X",
        "Y",
        "Z",
    ) == pytest.approx(0.0)


def test_negative_weight_is_rejected() -> None:
    statistics = TrigramStatistics()

    with pytest.raises(
        ValueError,
        match="weight must be non-negative",
    ):
        statistics.record(
            "a",
            "b",
            "c",
            weight=-1.0,
        )


@pytest.mark.parametrize(
    "characters",
    (
        ("", "b", "c"),
        ("ab", "c", "d"),
        ("a", "", "c"),
        ("a", "bc", "d"),
        ("a", "b", ""),
        ("a", "b", "cd"),
    ),
)
def test_invalid_character_length_is_rejected(
    characters: tuple[str, str, str],
) -> None:
    statistics = TrigramStatistics()

    with pytest.raises(
        ValueError,
        match=(
            "trigram characters must contain "
            "exactly one character"
        ),
    ):
        statistics.record(
            *characters,
        )
