# tests/test_transition_score_normalizer.py

import pytest

from evaluator.transition_score_normalizer import (
    NormalizedTransitionScore,
    normalize_transition_score,
)


def test_normalized_transition_score_type():
    result = normalize_transition_score(
        total_cost=30.0,
        evaluated_weight=100.0,
    )

    assert isinstance(result, NormalizedTransitionScore)


def test_normalized_transition_score():
    result = normalize_transition_score(
        total_cost=30.0,
        evaluated_weight=100.0,
    )

    assert result.score == pytest.approx(0.3)


def test_normalization_is_independent_of_corpus_scale():
    small = normalize_transition_score(
        total_cost=30.0,
        evaluated_weight=100.0,
    )

    large = normalize_transition_score(
        total_cost=300.0,
        evaluated_weight=1000.0,
    )

    assert small.score == pytest.approx(large.score)


def test_zero_weight_returns_zero():
    result = normalize_transition_score(
        total_cost=0.0,
        evaluated_weight=0.0,
    )

    assert result.score == 0.0


def test_negative_weight_is_rejected():
    with pytest.raises(ValueError):
        normalize_transition_score(
            total_cost=10.0,
            evaluated_weight=-1.0,
        )


def test_total_cost_is_preserved():
    result = normalize_transition_score(
        total_cost=25.0,
        evaluated_weight=50.0,
    )

    assert result.total_cost == 25.0


def test_evaluated_weight_is_preserved():
    result = normalize_transition_score(
        total_cost=25.0,
        evaluated_weight=50.0,
    )

    assert result.evaluated_weight == 50.0


def test_normalized_transition_score_is_immutable():
    result = normalize_transition_score(
        total_cost=25.0,
        evaluated_weight=50.0,
    )

    with pytest.raises(AttributeError):
        result.total_cost = 100.0