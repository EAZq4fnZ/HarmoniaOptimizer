# tests/test_corpus_analyzer.py
from evaluator.corpus_analyzer import CorpusAnalyzer
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry


def test_analyze_corpus():
    corpus = Corpus(
        entries=(
            CorpusEntry("hello"),
            CorpusEntry("world"),
        )
    )

    analyzer = CorpusAnalyzer()

    statistics = analyzer.analyze(corpus)

    assert statistics.raw_count("h", "e") == 1
    assert statistics.raw_count("e", "l") == 1
    assert statistics.raw_count("l", "l") == 1
    assert statistics.raw_count("l", "o") == 1

    assert statistics.raw_count("w", "o") == 1
    assert statistics.raw_count("o", "r") == 1
    assert statistics.raw_count("r", "l") == 1
    assert statistics.raw_count("l", "d") == 1


def test_analyze_empty_text_entry():
    corpus = Corpus(
        entries=(
            CorpusEntry("a"),
        )
    )

    analyzer = CorpusAnalyzer()

    statistics = analyzer.analyze(corpus)

    assert statistics.raw_count("a", "a") == 0
    assert statistics.weighted_count("a", "a") == 0.0
    assert statistics.raw() == {}
    assert statistics.weighted() == {}


def test_analyze_can_be_reused():
    analyzer = CorpusAnalyzer()

    corpus1 = Corpus(
        entries=(
            CorpusEntry("hello"),
        )
    )

    corpus2 = Corpus(
        entries=(
            CorpusEntry("world"),
        )
    )

    statistics1 = analyzer.analyze(corpus1)

    assert statistics1.raw_count("h", "e") == 1

    statistics2 = analyzer.analyze(corpus2)

    assert statistics2.raw_count("w", "o") == 1
    assert statistics2.raw_count("h", "e") == 0


def test_analyze_applies_entry_weight():
    corpus = Corpus(
        entries=(
            CorpusEntry("hello", weight=10.0),
            CorpusEntry("world", weight=2.0),
        )
    )

    analyzer = CorpusAnalyzer()

    statistics = analyzer.analyze(corpus)

    assert statistics.weighted_count("h", "e") == 10.0
    assert statistics.weighted_count("e", "l") == 10.0
    assert statistics.weighted_count("w", "o") == 2.0
    assert statistics.weighted_count("o", "r") == 2.0


def test_analyze_combines_weighted_transitions():
    corpus = Corpus(
        entries=(
            CorpusEntry("hello", weight=10.0),
            CorpusEntry("hello", weight=2.0),
        )
    )

    analyzer = CorpusAnalyzer()

    statistics = analyzer.analyze(corpus)

    assert statistics.raw_count("h", "e") == 2
    assert statistics.weighted_count("h", "e") == 12.0