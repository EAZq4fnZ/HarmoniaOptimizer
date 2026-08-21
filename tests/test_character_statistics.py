# tests/test_character_statistics.py

from evaluator.character_statistics import CharacterStatistics


def test_add_character():
    statistics = CharacterStatistics()

    statistics.add(
        {
            "a": 2,
        }
    )

    assert statistics.raw_count("a") == 2
    assert statistics.weighted_count("a") == 2.0


def test_weighted_character():
    statistics = CharacterStatistics()

    statistics.add(
        {
            "a": 2,
        },
        weight=3.0,
    )

    assert statistics.raw_count("a") == 2
    assert statistics.weighted_count("a") == 6.0


def test_multiple_weights_accumulate():
    statistics = CharacterStatistics()

    statistics.add(
        {
            "a": 2,
        },
        weight=3.0,
    )

    statistics.add(
        {
            "a": 1,
        },
        weight=2.0,
    )

    assert statistics.raw_count("a") == 3
    assert statistics.weighted_count("a") == 8.0


def test_multiple_characters():
    statistics = CharacterStatistics()

    statistics.add(
        {
            "a": 2,
            "b": 3,
        }
    )

    assert statistics.raw_count("a") == 2
    assert statistics.raw_count("b") == 3


def test_unknown_character_returns_zero():
    statistics = CharacterStatistics()

    assert statistics.raw_count("x") == 0
    assert statistics.weighted_count("x") == 0.0


def test_raw_statistics():
    statistics = CharacterStatistics()

    statistics.add(
        {
            "a": 2,
            "b": 3,
        }
    )

    assert statistics.raw() == {
        "a": 2,
        "b": 3,
    }


def test_weighted_statistics():
    statistics = CharacterStatistics()

    statistics.add(
        {
            "a": 2,
            "b": 3,
        },
        weight=2.0,
    )

    assert statistics.weighted() == {
        "a": 4.0,
        "b": 6.0,
    }


def test_totals():
    statistics = CharacterStatistics()

    statistics.add(
        {
            "a": 2,
            "b": 3,
        },
        weight=2.0,
    )

    assert statistics.total_raw() == 5
    assert statistics.total_weighted() == 10.0


def test_clear():
    statistics = CharacterStatistics()

    statistics.add(
        {
            "a": 2,
            "b": 3,
        }
    )

    statistics.clear()

    assert statistics.total_raw() == 0
    assert statistics.total_weighted() == 0.0