# transition_statistics.py
from evaluator.transition_statistics import TransitionStatistics


def test_add_transition():
    statistics = TransitionStatistics()

    statistics.add(
        {
            ("h", "e"): 1,
            ("e", "l"): 1,
        }
    )

    assert statistics.raw_count("h", "e") == 1
    assert statistics.raw_count("e", "l") == 1

    assert statistics.weighted_count("h", "e") == 1.0
    assert statistics.weighted_count("e", "l") == 1.0


def test_weighted_transition():
    statistics = TransitionStatistics()

    statistics.add(
        {
            ("h", "e"): 2,
        },
        weight=10.0,
    )

    assert statistics.raw_count("h", "e") == 2
    assert statistics.weighted_count("h", "e") == 20.0


def test_multiple_weights_accumulate():
    statistics = TransitionStatistics()

    statistics.add(
        {
            ("h", "e"): 2,
        },
        weight=10.0,
    )

    statistics.add(
        {
            ("h", "e"): 3,
        },
        weight=2.0,
    )

    assert statistics.raw_count("h", "e") == 5
    assert statistics.weighted_count("h", "e") == 26.0


def test_unknown_transition_returns_zero():
    statistics = TransitionStatistics()

    assert statistics.raw_count("x", "y") == 0
    assert statistics.weighted_count("x", "y") == 0.0


def test_clear():
    statistics = TransitionStatistics()

    statistics.add(
        {
            ("h", "e"): 2,
        },
        weight=10.0,
    )

    statistics.clear()

    assert statistics.raw() == {}
    assert statistics.weighted() == {}


def test_evaluation_records():
    statistics = TransitionStatistics()

    statistics.add(
        {
            ("a", "b"): 3,
            ("C", "d"): 2,
        }
    )

    assert (
        statistics.evaluation_records()
        == (
            ("A", "B", 3, 3.0),
            ("C", "D", 2, 2.0),
        )
    )


def test_evaluation_records_are_cached():
    statistics = TransitionStatistics()

    statistics.add(
        {
            ("a", "b"): 3,
        }
    )

    first = (
        statistics.evaluation_records()
    )

    second = (
        statistics.evaluation_records()
    )

    assert first is second


def test_evaluation_record_cache_is_invalidated():
    statistics = TransitionStatistics()

    statistics.add(
        {
            ("a", "b"): 3,
        }
    )

    first = (
        statistics.evaluation_records()
    )

    statistics.add(
        {
            ("c", "d"): 2,
        }
    )

    second = (
        statistics.evaluation_records()
    )

    assert first is not second

    assert (
        ("C", "D", 2, 2.0)
        in second
    )

def test_affected_transition_indexes_by_letter() -> None:
    statistics = TransitionStatistics()

    statistics.add(
        {
            ("A", "B"): 10,
            ("C", "A"): 20,
            ("B", "C"): 30,
            ("A", "A"): 40,
        }
    )

    records = (
        statistics.indexed_evaluation_records()
    )

    affected = (
        statistics
        .affected_transition_indexes_by_letter()
    )

    assert len(affected) == 26

    a_index = ord("A") - ord("A")
    b_index = ord("B") - ord("A")
    c_index = ord("C") - ord("A")
    d_index = ord("D") - ord("A")

    a_records = {
        records[index][:2]
        for index in affected[a_index]
    }

    b_records = {
        records[index][:2]
        for index in affected[b_index]
    }

    c_records = {
        records[index][:2]
        for index in affected[c_index]
    }

    assert a_records == {
        (a_index, b_index),
        (c_index, a_index),
        (a_index, a_index),
    }

    assert b_records == {
        (a_index, b_index),
        (b_index, c_index),
    }

    assert c_records == {
        (c_index, a_index),
        (b_index, c_index),
    }

    assert affected[d_index] == ()

def test_affected_transition_indexes_cache_is_invalidated() -> None:
    statistics = TransitionStatistics()

    statistics.add(
        {
            ("A", "B"): 10,
        }
    )

    first = (
        statistics
        .affected_transition_indexes_by_letter()
    )

    statistics.add(
        {
            ("C", "A"): 20,
        }
    )

    second = (
        statistics
        .affected_transition_indexes_by_letter()
    )

    assert second is not first

    a_index = ord("A") - ord("A")

    assert len(first[a_index]) == 1
    assert len(second[a_index]) == 2