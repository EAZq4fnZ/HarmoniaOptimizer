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

def test_fast_score_combines_trigram_component():
    scorer = FastCandidateScorer(
        CandidateScoreWeights(
            transition_weight=2.0,
            trigram_weight=3.0,
            finger_load_weight=4.0,
        )
    )

    score = scorer.score(
        transition_total_cost=30.0,
        evaluated_transition_weight=100.0,
        finger_load_penalty=0.1,
        trigram_total_cost=20.0,
        evaluated_trigram_weight=100.0,
    )

    # transition:
    # 30 / 100 = 0.3
    # 0.3 * 2 = 0.6
    #
    # trigram:
    # 20 / 100 = 0.2
    # 0.2 * 3 = 0.6
    #
    # finger:
    # 0.1 * 4 = 0.4
    #
    # total = 1.6
    assert score == pytest.approx(
        1.6
    )


def test_fast_score_handles_zero_trigram_weight():
    scorer = FastCandidateScorer(
        CandidateScoreWeights(
            transition_weight=0.0,
            trigram_weight=5.0,
            finger_load_weight=0.0,
        )
    )

    score = scorer.score(
        transition_total_cost=100.0,
        evaluated_transition_weight=1.0,
        finger_load_penalty=100.0,
        trigram_total_cost=100.0,
        evaluated_trigram_weight=0.0,
    )

    assert score == 0.0


def test_fast_score_rejects_negative_trigram_evaluated_weight():
    scorer = FastCandidateScorer(
        CandidateScoreWeights()
    )

    with pytest.raises(
        ValueError,
        match="evaluated_trigram_weight must be non-negative",
    ):
        scorer.score(
            transition_total_cost=1.0,
            evaluated_transition_weight=1.0,
            finger_load_penalty=0.0,
            trigram_total_cost=1.0,
            evaluated_trigram_weight=-1.0,
        )


def test_fast_score_preserves_legacy_call():
    scorer = FastCandidateScorer(
        CandidateScoreWeights(
            transition_weight=2.0,
            trigram_weight=7.0,
            finger_load_weight=3.0,
        )
    )

    score = scorer.score(
        transition_total_cost=10.0,
        evaluated_transition_weight=5.0,
        finger_load_penalty=0.5,
    )

    # No trigram arguments:
    # trigram contribution must remain zero.
    assert score == pytest.approx(
        5.5
    )


def test_fast_score_matches_three_component_formula():
    weights = CandidateScoreWeights(
        transition_weight=1.7,
        trigram_weight=2.3,
        finger_load_weight=0.8,
    )

    scorer = FastCandidateScorer(
        weights
    )

    transition_total = 18.0
    transition_weight = 12.0

    trigram_total = -7.5
    trigram_weight = 5.0

    finger_penalty = 0.35

    expected = (
        (transition_total / transition_weight)
        * weights.transition_weight
        + (trigram_total / trigram_weight)
        * weights.trigram_weight
        + finger_penalty
        * weights.finger_load_weight
    )

    actual = scorer.score(
        transition_total_cost=transition_total,
        evaluated_transition_weight=transition_weight,
        finger_load_penalty=finger_penalty,
        trigram_total_cost=trigram_total,
        evaluated_trigram_weight=trigram_weight,
    )

    assert actual == pytest.approx(
        expected
    )
