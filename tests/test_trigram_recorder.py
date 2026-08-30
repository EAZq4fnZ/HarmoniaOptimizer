import pytest

from evaluator.trigram_recorder import TrigramRecorder
from evaluator.trigram_statistics import TrigramStatistics


def test_records_single_trigram() -> None:
    statistics = TrigramStatistics()
    recorder = TrigramRecorder()

    recorder.record(
        "the",
        statistics,
    )

    assert statistics.raw_count(
        "T",
        "H",
        "E",
    ) == 1


def test_records_overlapping_trigrams() -> None:
    statistics = TrigramStatistics()
    recorder = TrigramRecorder()

    recorder.record(
        "there",
        statistics,
    )

    assert tuple(
        statistics.evaluation_records()
    ) == (
        (
            "E",
            "R",
            "E",
            1,
            pytest.approx(1.0),
        ),
        (
            "H",
            "E",
            "R",
            1,
            pytest.approx(1.0),
        ),
        (
            "T",
            "H",
            "E",
            1,
            pytest.approx(1.0),
        ),
    )


def test_normalizes_lowercase_text() -> None:
    statistics = TrigramStatistics()
    recorder = TrigramRecorder()

    recorder.record(
        "The",
        statistics,
    )

    assert statistics.raw_count(
        "T",
        "H",
        "E",
    ) == 1


def test_applies_weight_to_every_trigram() -> None:
    statistics = TrigramStatistics()
    recorder = TrigramRecorder()

    recorder.record(
        "there",
        statistics,
        weight=0.5,
    )

    assert statistics.total_raw_count == 3
    assert statistics.total_weighted_count == pytest.approx(
        1.5
    )


def test_non_letter_breaks_trigram_sequence() -> None:
    statistics = TrigramStatistics()
    recorder = TrigramRecorder()

    recorder.record(
        "the cat",
        statistics,
    )

    assert statistics.raw_count(
        "T",
        "H",
        "E",
    ) == 1

    assert statistics.raw_count(
        "C",
        "A",
        "T",
    ) == 1

    assert statistics.raw_count(
        "E",
        "C",
        "A",
    ) == 0

    assert statistics.total_raw_count == 2


def test_punctuation_breaks_trigram_sequence() -> None:
    statistics = TrigramStatistics()
    recorder = TrigramRecorder()

    recorder.record(
        "abc.def",
        statistics,
    )

    assert statistics.raw_count(
        "A",
        "B",
        "C",
    ) == 1

    assert statistics.raw_count(
        "D",
        "E",
        "F",
    ) == 1

    assert statistics.total_raw_count == 2


def test_short_text_records_nothing() -> None:
    statistics = TrigramStatistics()
    recorder = TrigramRecorder()

    recorder.record(
        "",
        statistics,
    )
    recorder.record(
        "a",
        statistics,
    )
    recorder.record(
        "ab",
        statistics,
    )

    assert statistics.total_raw_count == 0
    assert len(statistics) == 0


def test_repeated_trigram_accumulates() -> None:
    statistics = TrigramStatistics()
    recorder = TrigramRecorder()

    recorder.record(
        "aaaa",
        statistics,
    )

    assert statistics.raw_count(
        "A",
        "A",
        "A",
    ) == 2


def test_negative_weight_is_rejected() -> None:
    statistics = TrigramStatistics()
    recorder = TrigramRecorder()

    with pytest.raises(
        ValueError,
        match="weight must be non-negative",
    ):
        recorder.record(
            "abc",
            statistics,
            weight=-1.0,
        )
