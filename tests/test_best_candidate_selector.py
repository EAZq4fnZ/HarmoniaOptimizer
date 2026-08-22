# tests/test_best_candidate_selector.py

from models.candidate_evaluation import CandidateEvaluation
from models.candidate_score import CandidateScore, CandidateScoreWeights
from models.constraint_evaluation import ConstraintEvaluation
from models.constraint_violation import ConstraintViolation
from models.layout import Layout
from models.swap_candidate import SwapCandidate
from models.swap_candidate_evaluation import SwapCandidateEvaluation
from models.swap_move import SwapMove
from optimizer.best_candidate_selector import BestCandidateSelector


def make_layout(
    name: str = "test",
) -> Layout:
    mapping = {
        chr(ord("A") + index): f"P{index}"
        for index in range(26)
    }

    return Layout(
        name=name,
        version="1",
        layer="L0",
        description="best candidate selector test",
        mapping=mapping,
    )


def make_candidate_score(
    transition_score: float,
    finger_load_score: float = 0.0,
) -> CandidateScore:
    return CandidateScore(
        transition_score=transition_score,
        finger_load_score=finger_load_score,
        weights=CandidateScoreWeights(
            transition_weight=1.0,
            finger_load_weight=1.0,
        ),
    )


def make_valid_evaluation(
    transition_score: float,
    name: str = "test",
    finger_load_score: float = 0.0,
) -> CandidateEvaluation:
    return CandidateEvaluation(
        layout=make_layout(name),
        constraint_evaluation=ConstraintEvaluation(
            violations=(),
        ),
        layout_evaluation=None,
        candidate_score=make_candidate_score(
            transition_score=transition_score,
            finger_load_score=finger_load_score,
        ),
    )


def make_invalid_evaluation(
    transition_score: float,
) -> CandidateEvaluation:
    violation = ConstraintViolation(
        constraint="test_constraint",
        message="test violation",
    )

    return CandidateEvaluation(
        layout=make_layout("invalid"),
        constraint_evaluation=ConstraintEvaluation(
            violations=(violation,),
        ),
        layout_evaluation=None,
        candidate_score=make_candidate_score(
            transition_score=transition_score,
        ),
    )


def make_unscored_evaluation() -> CandidateEvaluation:
    return CandidateEvaluation(
        layout=make_layout("unscored"),
        constraint_evaluation=ConstraintEvaluation(
            violations=(),
        ),
        layout_evaluation=None,
        candidate_score=None,
    )


def test_select_returns_lowest_score():
    selector = BestCandidateSelector()

    high = make_valid_evaluation(
        10.0,
        "high",
    )
    low = make_valid_evaluation(
        5.0,
        "low",
    )
    middle = make_valid_evaluation(
        7.0,
        "middle",
    )

    result = selector.select(
        (high, low, middle)
    )

    assert result == low


def test_select_ignores_invalid_candidate():
    selector = BestCandidateSelector()

    valid = make_valid_evaluation(10.0)
    invalid = make_invalid_evaluation(1.0)

    result = selector.select(
        (valid, invalid)
    )

    assert result == valid


def test_select_ignores_candidate_without_score():
    selector = BestCandidateSelector()

    valid = make_valid_evaluation(10.0)
    unscored = make_unscored_evaluation()

    result = selector.select(
        (unscored, valid)
    )

    assert result == valid


def test_select_returns_none_for_empty_input():
    selector = BestCandidateSelector()

    result = selector.select(())

    assert result is None


def test_select_returns_none_when_all_invalid():
    selector = BestCandidateSelector()

    result = selector.select(
        (
            make_invalid_evaluation(1.0),
            make_invalid_evaluation(2.0),
        )
    )

    assert result is None


def test_select_returns_none_when_all_unscored():
    selector = BestCandidateSelector()

    result = selector.select(
        (
            make_unscored_evaluation(),
            make_unscored_evaluation(),
        )
    )

    assert result is None


def test_select_single_valid_candidate():
    selector = BestCandidateSelector()

    candidate = make_valid_evaluation(5.0)

    result = selector.select(
        (candidate,)
    )

    assert result == candidate


def test_select_preserves_first_candidate_on_tie():
    selector = BestCandidateSelector()

    first = make_valid_evaluation(
        5.0,
        "first",
    )
    second = make_valid_evaluation(
        5.0,
        "second",
    )

    result = selector.select(
        (first, second)
    )

    assert result == first


def test_select_uses_total_candidate_score():
    selector = BestCandidateSelector()

    first = make_valid_evaluation(
        transition_score=3.0,
        finger_load_score=4.0,
        name="first",
    )

    second = make_valid_evaluation(
        transition_score=5.0,
        finger_load_score=1.0,
        name="second",
    )

    result = selector.select(
        (first, second)
    )

    # first:
    # 3.0 + 4.0 = 7.0
    #
    # second:
    # 5.0 + 1.0 = 6.0

    assert result == second


def test_select_accepts_generator():
    selector = BestCandidateSelector()

    candidates = (
        make_valid_evaluation(
            score,
            f"candidate-{score}",
        )
        for score in (10.0, 3.0, 7.0)
    )

    result = selector.select(candidates)

    assert result is not None
    assert result.score == 3.0


def make_swap_candidate_evaluation(
    score: float,
    first_letter: str,
    second_letter: str,
    name: str,
) -> SwapCandidateEvaluation:
    evaluation = make_valid_evaluation(
        transition_score=score,
        name=name,
    )

    candidate = SwapCandidate(
        move=SwapMove(
            first_letter=first_letter,
            second_letter=second_letter,
        ),
        layout=evaluation.layout,
    )

    return SwapCandidateEvaluation(
        candidate=candidate,
        evaluation=evaluation,
    )


def test_select_swap_candidate_returns_lowest_score():
    selector = BestCandidateSelector()

    high = make_swap_candidate_evaluation(
        score=10.0,
        first_letter="A",
        second_letter="B",
        name="high",
    )

    low = make_swap_candidate_evaluation(
        score=3.0,
        first_letter="C",
        second_letter="D",
        name="low",
    )

    middle = make_swap_candidate_evaluation(
        score=7.0,
        first_letter="E",
        second_letter="F",
        name="middle",
    )

    result = selector.select_swap_candidate(
        (high, low, middle)
    )

    assert result == low
    assert result.move == low.move


def test_select_swap_candidate_preserves_move():
    selector = BestCandidateSelector()

    candidate = make_swap_candidate_evaluation(
        score=3.0,
        first_letter="A",
        second_letter="T",
        name="candidate",
    )

    result = selector.select_swap_candidate(
        (candidate,)
    )

    assert result is not None
    assert result.move.first_letter == "A"
    assert result.move.second_letter == "T"


def test_select_swap_candidate_returns_none_for_empty_input():
    selector = BestCandidateSelector()

    result = selector.select_swap_candidate(())

    assert result is None


def test_select_swap_candidate_preserves_first_on_tie():
    selector = BestCandidateSelector()

    first = make_swap_candidate_evaluation(
        score=5.0,
        first_letter="A",
        second_letter="B",
        name="first",
    )

    second = make_swap_candidate_evaluation(
        score=5.0,
        first_letter="C",
        second_letter="D",
        name="second",
    )

    result = selector.select_swap_candidate(
        (first, second)
    )

    assert result == first
    assert result.move == first.move


def test_select_swap_candidate_accepts_generator():
    selector = BestCandidateSelector()

    evaluations = (
        make_swap_candidate_evaluation(
            score=score,
            first_letter=first_letter,
            second_letter=second_letter,
            name=name,
        )
        for score, first_letter, second_letter, name in (
            (10.0, "A", "B", "high"),
            (2.0, "C", "D", "low"),
            (7.0, "E", "F", "middle"),
        )
    )

    result = selector.select_swap_candidate(
        evaluations
    )

    assert result is not None
    assert result.score == 2.0
    assert result.move == SwapMove(
        first_letter="C",
        second_letter="D",
    )