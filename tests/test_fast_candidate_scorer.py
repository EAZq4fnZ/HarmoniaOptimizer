# tests/test_fast_candidate_scorer.py

import pytest

from evaluator.fast_candidate_scorer import (
    FastCandidateScorer,
)
from models.candidate_score import (
    CandidateScoreWeights,
)


def test_fast_score_combines_components():
    scorer = FastCandidateScorer(
        CandidateScoreWeights(
            transition_weight=2.0,
            finger_load_weight=3.0,
        )
    )

    score = scorer.score(
        transition_total_cost=10.0,
        evaluated_transition_weight=5.0,
        finger_load_penalty=0.5,
    )

    assert score == pytest.approx(
        5.5
    )


def test_fast_score_handles_zero_transition_weight():
    scorer = FastCandidateScorer(
        CandidateScoreWeights(
            transition_weight=1.0,
            finger_load_weight=1.0,
        )
    )

    score = scorer.score(
        transition_total_cost=10.0,
        evaluated_transition_weight=0.0,
        finger_load_penalty=0.25,
    )

    assert score == pytest.approx(
        0.25
    )


def test_fast_score_rejects_negative_evaluated_weight():
    scorer = FastCandidateScorer(
        CandidateScoreWeights()
    )

    with pytest.raises(
        ValueError,
    ):
        scorer.score(
            transition_total_cost=1.0,
            evaluated_transition_weight=-1.0,
            finger_load_penalty=0.0,
        )


def test_fast_score_matches_candidate_score_formula():
    weights = CandidateScoreWeights(
        transition_weight=1.7,
        finger_load_weight=0.8,
    )

    scorer = FastCandidateScorer(
        weights
    )

    transition_total = 18.0
    evaluated_weight = 12.0
    finger_penalty = 0.35

    expected = (
        (transition_total / evaluated_weight)
        * weights.transition_weight
        + finger_penalty
        * weights.finger_load_weight
    )

    actual = scorer.score(
        transition_total_cost=transition_total,
        evaluated_transition_weight=evaluated_weight,
        finger_load_penalty=finger_penalty,
    )

    assert actual == pytest.approx(
        expected
    )