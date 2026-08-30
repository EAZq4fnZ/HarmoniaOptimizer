# tests/test_candidate_score.py

import pytest

from models.candidate_score import (
    CandidateScore,
    CandidateScoreWeights,
)


def test_default_weights():
    weights = CandidateScoreWeights()

    assert weights.transition_weight == 1.0
    assert weights.finger_load_weight == 1.0


def test_custom_weights():
    weights = CandidateScoreWeights(
        transition_weight=2.0,
        finger_load_weight=3.0,
    )

    assert weights.transition_weight == 2.0
    assert weights.finger_load_weight == 3.0


def test_negative_transition_weight_is_rejected():
    with pytest.raises(ValueError):
        CandidateScoreWeights(
            transition_weight=-1.0,
        )


def test_negative_finger_load_weight_is_rejected():
    with pytest.raises(ValueError):
        CandidateScoreWeights(
            finger_load_weight=-1.0,
        )


def test_weighted_transition_score():
    score = CandidateScore(
        transition_score=2.0,
        finger_load_score=0.5,
        weights=CandidateScoreWeights(
            transition_weight=3.0,
            finger_load_weight=1.0,
        ),
    )

    assert score.weighted_transition_score == 6.0


def test_weighted_finger_load_score():
    score = CandidateScore(
        transition_score=2.0,
        finger_load_score=0.5,
        weights=CandidateScoreWeights(
            transition_weight=1.0,
            finger_load_weight=4.0,
        ),
    )

    assert score.weighted_finger_load_score == 2.0


def test_total_score():
    score = CandidateScore(
        transition_score=2.0,
        finger_load_score=0.5,
        weights=CandidateScoreWeights(
            transition_weight=3.0,
            finger_load_weight=4.0,
        ),
    )

    assert score.total == 8.0


def test_zero_weights():
    score = CandidateScore(
        transition_score=100.0,
        finger_load_score=100.0,
        weights=CandidateScoreWeights(
            transition_weight=0.0,
            finger_load_weight=0.0,
        ),
    )

    assert score.total == 0.0


def test_candidate_score_is_immutable():
    score = CandidateScore(
        transition_score=1.0,
        finger_load_score=0.5,
        weights=CandidateScoreWeights(),
    )

    with pytest.raises(AttributeError):
        score.transition_score = 2.0

def test_default_position_weight_preserves_legacy_total():
    weights = CandidateScoreWeights(
        transition_weight=2.0,
        trigram_weight=3.0,
        finger_load_weight=4.0,
    )

    score = CandidateScore(
        transition_score=0.5,
        finger_load_score=0.25,
        weights=weights,
        trigram_score=-0.2,
        position_score=999.0,
    )

    expected = (
        0.5 * 2.0
        + (-0.2) * 3.0
        + 0.25 * 4.0
    )

    assert weights.position_weight == 0.0
    assert score.weighted_position_score == 0.0
    assert score.total == pytest.approx(
        expected
    )
