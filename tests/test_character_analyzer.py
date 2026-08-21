# tests/test_character_analyzer.py

from evaluator.character_analyzer import CharacterAnalyzer
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry


def test_analyze_single_entry():
    corpus = Corpus(
        entries=(
            CorpusEntry("hello"),
        )
    )

    analyzer = CharacterAnalyzer()

    statistics = analyzer.analyze(corpus)

    assert statistics.raw_count("h") == 1
    assert statistics.raw_count("e") == 1
    assert statistics.raw_count("l") == 2
    assert statistics.raw_count("o") == 1


def test_analyze_multiple_entries():
    corpus = Corpus(
        entries=(
            CorpusEntry("hello"),
            CorpusEntry("world"),
        )
    )

    analyzer = CharacterAnalyzer()

    statistics = analyzer.analyze(corpus)

    assert statistics.raw_count("l") == 3
    assert statistics.raw_count("o") == 2


def test_analyze_applies_entry_weight():
    corpus = Corpus(
        entries=(
            CorpusEntry(
                "aa",
                weight=3.0,
            ),
        )
    )

    analyzer = CharacterAnalyzer()

    statistics = analyzer.analyze(corpus)

    assert statistics.raw_count("a") == 2
    assert statistics.weighted_count("a") == 6.0


def test_analyze_combines_weighted_entries():
    corpus = Corpus(
        entries=(
            CorpusEntry(
                "aa",
                weight=3.0,
            ),
            CorpusEntry(
                "a",
                weight=2.0,
            ),
        )
    )

    analyzer = CharacterAnalyzer()

    statistics = analyzer.analyze(corpus)

    assert statistics.raw_count("a") == 3
    assert statistics.weighted_count("a") == 8.0


def test_analyze_is_case_insensitive():
    corpus = Corpus(
        entries=(
            CorpusEntry("AaA"),
        )
    )

    analyzer = CharacterAnalyzer()

    statistics = analyzer.analyze(corpus)

    assert statistics.raw_count("a") == 3
    assert statistics.raw_count("A") == 0


def test_analyze_preserves_unsupported_characters():
    corpus = Corpus(
        entries=(
            CorpusEntry("a a."),
        )
    )

    analyzer = CharacterAnalyzer()

    statistics = analyzer.analyze(corpus)

    assert statistics.raw_count("a") == 2
    assert statistics.raw_count(" ") == 1
    assert statistics.raw_count(".") == 1


def test_analyze_totals():
    corpus = Corpus(
        entries=(
            CorpusEntry(
                "abc",
                weight=2.0,
            ),
        )
    )

    analyzer = CharacterAnalyzer()

    statistics = analyzer.analyze(corpus)

    assert statistics.total_raw() == 3
    assert statistics.total_weighted() == 6.0