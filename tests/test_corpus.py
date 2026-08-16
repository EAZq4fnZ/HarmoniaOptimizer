# tests/test_corpus.py
import pytest

from models.corpus import Corpus
from models.corpus_entry import CorpusEntry


def test_corpus_entry():
    entry = CorpusEntry(
        text="hello",
        weight=2.0,
    )

    assert entry.text == "hello"
    assert entry.weight == 2.0


def test_corpus_entry_default_weight():
    entry = CorpusEntry(text="hello")

    assert entry.weight == 1.0


def test_corpus_entry_rejects_empty_text():
    with pytest.raises(
        ValueError,
        match="Corpus entry text must not be empty",
    ):
        CorpusEntry(text="")


def test_corpus_entry_rejects_invalid_weight():
    with pytest.raises(
        ValueError,
        match="Corpus entry weight must be greater than 0",
    ):
        CorpusEntry(
            text="hello",
            weight=0,
        )


def test_corpus():
    entries = (
        CorpusEntry("hello"),
        CorpusEntry("world", weight=2.0),
    )

    corpus = Corpus(entries=entries)

    assert len(corpus.entries) == 2


def test_corpus_total_weight():
    entries = (
        CorpusEntry("hello", weight=1.0),
        CorpusEntry("world", weight=2.0),
    )

    corpus = Corpus(entries=entries)

    assert corpus.total_weight == 3.0


def test_corpus_total_characters():
    entries = (
        CorpusEntry("hello"),
        CorpusEntry("world"),
    )

    corpus = Corpus(entries=entries)

    assert corpus.total_characters == 10


def test_corpus_rejects_empty_entries():
    with pytest.raises(
        ValueError,
        match="Corpus must contain at least one entry",
    ):
        Corpus(entries=())