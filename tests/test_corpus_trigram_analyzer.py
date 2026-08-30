import pytest

from evaluator.corpus_analyzer import CorpusAnalyzer
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry


def test_analyze_trigrams_records_each_entry() -> None:
    corpus = Corpus(
        entries=(
            CorpusEntry("hello"),
            CorpusEntry("world"),
        )
    )

    analyzer = CorpusAnalyzer()

    statistics = analyzer.analyze_trigrams(
        corpus
    )

    assert statistics.raw_count(
        "H",
        "E",
        "L",
    ) == 1

    assert statistics.raw_count(
        "E",
        "L",
        "L",
    ) == 1

    assert statistics.raw_count(
        "L",
        "L",
        "O",
    ) == 1

    assert statistics.raw_count(
        "W",
        "O",
        "R",
    ) == 1

    assert statistics.raw_count(
        "O",
        "R",
        "L",
    ) == 1

    assert statistics.raw_count(
        "R",
        "L",
        "D",
    ) == 1


def test_analyze_trigrams_does_not_cross_entries() -> None:
    corpus = Corpus(
        entries=(
            CorpusEntry("ab"),
            CorpusEntry("cde"),
        )
    )

    analyzer = CorpusAnalyzer()

    statistics = analyzer.analyze_trigrams(
        corpus
    )

    assert statistics.raw_count(
        "A",
        "B",
        "C",
    ) == 0

    assert statistics.raw_count(
        "C",
        "D",
        "E",
    ) == 1

    assert statistics.total_raw_count == 1


def test_analyze_trigrams_applies_entry_weight() -> None:
    corpus = Corpus(
        entries=(
            CorpusEntry(
                "hello",
                weight=10.0,
            ),
            CorpusEntry(
                "world",
                weight=2.0,
            ),
        )
    )

    analyzer = CorpusAnalyzer()

    statistics = analyzer.analyze_trigrams(
        corpus
    )

    assert statistics.weighted_count(
        "H",
        "E",
        "L",
    ) == pytest.approx(10.0)

    assert statistics.weighted_count(
        "E",
        "L",
        "L",
    ) == pytest.approx(10.0)

    assert statistics.weighted_count(
        "W",
        "O",
        "R",
    ) == pytest.approx(2.0)

    assert statistics.weighted_count(
        "O",
        "R",
        "L",
    ) == pytest.approx(2.0)


def test_analyze_trigrams_combines_weighted_entries() -> None:
    corpus = Corpus(
        entries=(
            CorpusEntry(
                "hello",
                weight=10.0,
            ),
            CorpusEntry(
                "hello",
                weight=2.0,
            ),
        )
    )

    analyzer = CorpusAnalyzer()

    statistics = analyzer.analyze_trigrams(
        corpus
    )

    assert statistics.raw_count(
        "H",
        "E",
        "L",
    ) == 2

    assert statistics.weighted_count(
        "H",
        "E",
        "L",
    ) == pytest.approx(12.0)


def test_analyze_trigrams_can_be_reused() -> None:
    analyzer = CorpusAnalyzer()

    first = analyzer.analyze_trigrams(
        Corpus(
            entries=(
                CorpusEntry("hello"),
            )
        )
    )

    second = analyzer.analyze_trigrams(
        Corpus(
            entries=(
                CorpusEntry("world"),
            )
        )
    )

    assert first.raw_count(
        "H",
        "E",
        "L",
    ) == 1

    assert second.raw_count(
        "W",
        "O",
        "R",
    ) == 1

    assert second.raw_count(
        "H",
        "E",
        "L",
    ) == 0


def test_existing_analyze_remains_transition_only() -> None:
    corpus = Corpus(
        entries=(
            CorpusEntry("hello"),
        )
    )

    analyzer = CorpusAnalyzer()

    statistics = analyzer.analyze(
        corpus
    )

    assert statistics.raw_count(
        "h",
        "e",
    ) == 1

    assert statistics.raw_count(
        "e",
        "l",
    ) == 1
