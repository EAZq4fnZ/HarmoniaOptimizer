# tests/test_finger_load_evaluator.py

from evaluator.character_statistics import CharacterStatistics
from evaluator.finger_load_evaluator import FingerLoadEvaluator
from models.enums import Finger, Hand
from models.layout import Layout


def make_layout() -> Layout:
    return Layout(
        name="Test Layout",
        version="0.1.0",
        layer="L0",
        description="Finger load evaluator test layout",
        mapping={
            "A": "L-M-H-2",
            "B": "L-M-T-2",
            "C": "L-R-H-1",
            "D": "L-R-T-1",
            "E": "L-I-H-3",
            "F": "L-I-T-3",
            "G": "L-I-H-4",
            "H": "L-I-T-4",
            "I": "L-M-B-2",
            "J": "R-I-H-4",
            "K": "R-I-T-4",
            "L": "R-I-H-3",
            "M": "R-I-T-3",
            "N": "R-M-H-2",
            "O": "R-M-T-2",
            "P": "R-R-H-1",
            "Q": "R-R-T-1",
            "R": "L-P-H-0",
            "S": "L-P-T-0",
            "T": "L-P-B-0",
            "U": "R-P-H-0",
            "V": "R-P-T-0",
            "W": "R-P-B-0",
            "X": "L-I-B-3",
            "Y": "R-I-B-3",
            "Z": "R-M-B-2",
        },
    )


def find_load(
    loads,
    hand: Hand,
    finger: Finger,
):
    return next(
        load
        for load in loads
        if load.hand == hand
        and load.finger == finger
    )


def test_evaluate_single_character():
    statistics = CharacterStatistics()
    statistics.add(
        {"a": 3},
    )

    evaluator = FingerLoadEvaluator()

    loads = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    load = find_load(
        loads,
        Hand.LEFT,
        Finger.MIDDLE,
    )

    assert load.raw_count == 3
    assert load.weighted_count == 3.0


def test_evaluate_combines_same_finger():
    statistics = CharacterStatistics()
    statistics.add(
        {
            "a": 3,
            "b": 2,
        }
    )

    evaluator = FingerLoadEvaluator()

    loads = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    load = find_load(
        loads,
        Hand.LEFT,
        Finger.MIDDLE,
    )

    assert load.raw_count == 5
    assert load.weighted_count == 5.0


def test_evaluate_separates_fingers():
    statistics = CharacterStatistics()
    statistics.add(
        {
            "a": 3,
            "c": 2,
        }
    )

    evaluator = FingerLoadEvaluator()

    loads = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    middle = find_load(
        loads,
        Hand.LEFT,
        Finger.MIDDLE,
    )

    ring = find_load(
        loads,
        Hand.LEFT,
        Finger.RING,
    )

    assert middle.raw_count == 3
    assert ring.raw_count == 2


def test_evaluate_separates_hands():
    statistics = CharacterStatistics()
    statistics.add(
        {
            "e": 3,
            "l": 2,
        }
    )

    evaluator = FingerLoadEvaluator()

    loads = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    left = find_load(
        loads,
        Hand.LEFT,
        Finger.INDEX,
    )

    right = find_load(
        loads,
        Hand.RIGHT,
        Finger.INDEX,
    )

    assert left.raw_count == 3
    assert right.raw_count == 2


def test_evaluate_applies_weight():
    statistics = CharacterStatistics()

    statistics.add(
        {"a": 2},
        weight=3.0,
    )

    evaluator = FingerLoadEvaluator()

    loads = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    load = find_load(
        loads,
        Hand.LEFT,
        Finger.MIDDLE,
    )

    assert load.raw_count == 2
    assert load.weighted_count == 6.0


def test_unsupported_character_is_ignored():
    statistics = CharacterStatistics()

    statistics.add(
        {
            "a": 2,
            ".": 10,
            " ": 20,
        }
    )

    evaluator = FingerLoadEvaluator()

    loads = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    assert sum(
        load.raw_count
        for load in loads
    ) == 2


def test_finger_load_is_immutable():
    statistics = CharacterStatistics()
    statistics.add({"a": 1})

    evaluator = FingerLoadEvaluator()

    loads = evaluator.evaluate(
        make_layout(),
        statistics,
    )

    load = find_load(
        loads,
        Hand.LEFT,
        Finger.MIDDLE,
    )

    try:
        load.raw_count = 100
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "FingerLoad must be immutable."
        )