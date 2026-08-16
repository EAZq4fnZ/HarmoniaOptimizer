# tests/test_transition_recorder.py
from evaluator.transition_recorder import TransitionRecorder
from models.corpus_entry import CorpusEntry


def test_record_single_word():
    recorder = TransitionRecorder()

    recorder.record("hello")

    assert recorder.count("h", "e") == 1
    assert recorder.count("e", "l") == 1
    assert recorder.count("l", "l") == 1
    assert recorder.count("l", "o") == 1


def test_total_transitions():
    recorder = TransitionRecorder()

    recorder.record("hello")

    assert recorder.total() == 4


def test_repeated_transitions():
    recorder = TransitionRecorder()

    recorder.record("aaaa")

    assert recorder.count("a", "a") == 3
    assert recorder.total() == 3


def test_multiple_records_accumulate():
    recorder = TransitionRecorder()

    recorder.record("hello")
    recorder.record("hello")

    assert recorder.count("h", "e") == 2
    assert recorder.count("e", "l") == 2
    assert recorder.count("l", "l") == 2
    assert recorder.count("l", "o") == 2
    assert recorder.total() == 8


def test_transitions():
    recorder = TransitionRecorder()

    recorder.record("hello")

    assert recorder.transitions() == {
        ("h", "e"): 1,
        ("e", "l"): 1,
        ("l", "l"): 1,
        ("l", "o"): 1,
    }


def test_empty_text():
    recorder = TransitionRecorder()

    recorder.record("")

    assert recorder.total() == 0


def test_single_character():
    recorder = TransitionRecorder()

    recorder.record("a")

    assert recorder.total() == 0


def test_clear():
    recorder = TransitionRecorder()

    recorder.record("hello")
    recorder.clear()

    assert recorder.total() == 0
    assert recorder.transitions() == {}


def test_record_entry():
    recorder = TransitionRecorder()

    entry = CorpusEntry(text="hello")

    recorder.record_entry(entry)

    assert recorder.count("h", "e") == 1
    assert recorder.count("e", "l") == 1
    assert recorder.count("l", "l") == 1
    assert recorder.count("l", "o") == 1
    assert recorder.total() == 4
