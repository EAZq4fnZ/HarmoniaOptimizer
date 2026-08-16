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