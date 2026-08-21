# tests/test_best_candidate_selector.py

from models.candidate_evaluation import CandidateEvaluation
from models.candidate_score import CandidateScore, CandidateScoreWeights
from models.constraint_evaluation import ConstraintEvaluation
from models.constraint_violation import ConstraintViolation
from models.layout import Layout
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