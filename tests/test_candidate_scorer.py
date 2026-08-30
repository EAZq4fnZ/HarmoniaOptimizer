# tests/test_candidate_scorer.py

import pytest

from evaluator.candidate_scorer import CandidateScorer
from models.candidate_score import CandidateScoreWeights
from models.enums import Finger, Hand
from models.finger_load_evaluation import FingerLoadEvaluation
from models.layout_evaluation import LayoutEvaluation
from models.trigram_layout_evaluation import (
    TrigramLayoutEvaluation,
)


def make_layout_evaluation(
    *,
    total_cost: float = 30.0,
    evaluated_weight: float = 100.0,
) -> LayoutEvaluation:
    return LayoutEvaluation(
        total_cost=total_cost,
        evaluated_weight=evaluated_weight,
        skipped_weight=0.0,
        transitions=(),
    )


def make_finger_evaluation(
    *,
    penalty: float,
) -> FingerLoadEvaluation:
    return FingerLoadEvaluation(
        hand=Hand.LEFT,
        finger=Finger.INDEX,
        actual_ratio=0.3,
        target_ratio=0.2,
        tolerance=0.0,
        excess_ratio=penalty,
        penalty=penalty,
    )

def make_trigram_layout_evaluation(
    *,
    total_cost: float = 20.0,
    evaluated_weight: float = 100.0,
) -> TrigramLayoutEvaluation:
    return TrigramLayoutEvaluation(
        total_cost=total_cost,
        evaluated_weight=evaluated_weight,
        skipped_weight=0.0,
        trigrams=(),
    )


def test_transition_score_is_normalized():
    scorer = CandidateScorer(
        CandidateScoreWeights()
    )

    result = scorer.score(
        make_layout_evaluation(
            total_cost=30.0,
            evaluated_weight=100.0,
        ),
        (),
    )

    assert result.transition_score == pytest.approx(0.3)


def test_finger_load_penalties_are_summed():
    scorer = CandidateScorer(
        CandidateScoreWeights()
    )

    finger_evaluations = (
        make_finger_evaluation(penalty=0.1),
        make_finger_evaluation(penalty=0.2),
    )

    result = scorer.score(
        make_layout_evaluation(),
        finger_evaluations,
    )

    assert result.finger_load_score == pytest.approx(0.3)


def test_empty_finger_load_has_zero_score():
    scorer = CandidateScorer(
        CandidateScoreWeights()
    )

    result = scorer.score(
        make_layout_evaluation(),
        (),
    )

    assert result.finger_load_score == 0.0


def test_zero_transition_weight_has_zero_transition_score():
    scorer = CandidateScorer(
        CandidateScoreWeights()
    )

    result = scorer.score(
        make_layout_evaluation(
            total_cost=0.0,
            evaluated_weight=0.0,
        ),
        (),
    )

    assert result.transition_score == 0.0


def test_score_weights_are_applied():
    scorer = CandidateScorer(
        CandidateScoreWeights(
            transition_weight=2.0,
            finger_load_weight=4.0,
        )
    )

    result = scorer.score(
        make_layout_evaluation(
            total_cost=30.0,
            evaluated_weight=100.0,
        ),
        (
            make_finger_evaluation(
                penalty=0.1
            ),
        ),
    )

    # transition:
    # 30 / 100 = 0.3
    # 0.3 * 2 = 0.6
    #
    # finger:
    # 0.1 * 4 = 0.4
    #
    # total = 1.0
    assert result.total == pytest.approx(1.0)


def test_transition_normalization_is_scale_independent():
    scorer = CandidateScorer(
        CandidateScoreWeights()
    )

    small = scorer.score(
        make_layout_evaluation(
            total_cost=30.0,
            evaluated_weight=100.0,
        ),
        (),
    )

    large = scorer.score(
        make_layout_evaluation(
            total_cost=300.0,
            evaluated_weight=1000.0,
        ),
        (),
    )

    assert small.transition_score == pytest.approx(
        large.transition_score
    )


def test_weights_are_exposed():
    weights = CandidateScoreWeights(
        transition_weight=2.0,
        finger_load_weight=3.0,
    )

    scorer = CandidateScorer(weights)

    assert scorer.weights == weights

def test_trigram_score_is_normalized():
    scorer = CandidateScorer(
        CandidateScoreWeights(
            trigram_weight=1.0,
        )
    )

    result = scorer.score(
        make_layout_evaluation(),
        (),
        trigram_layout_evaluation=(
            make_trigram_layout_evaluation(
                total_cost=20.0,
                evaluated_weight=100.0,
            )
        ),
    )

    assert result.trigram_score == pytest.approx(
        0.2
    )


def test_trigram_weight_is_applied():
    scorer = CandidateScorer(
        CandidateScoreWeights(
            transition_weight=2.0,
            trigram_weight=3.0,
            finger_load_weight=4.0,
        )
    )

    result = scorer.score(
        make_layout_evaluation(
            total_cost=30.0,
            evaluated_weight=100.0,
        ),
        (
            make_finger_evaluation(
                penalty=0.1
            ),
        ),
        trigram_layout_evaluation=(
            make_trigram_layout_evaluation(
                total_cost=20.0,
                evaluated_weight=100.0,
            )
        ),
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
    assert result.total == pytest.approx(
        1.6
    )


def test_zero_trigram_weight_preserves_total():
    scorer = CandidateScorer(
        CandidateScoreWeights(
            transition_weight=2.0,
            trigram_weight=0.0,
            finger_load_weight=4.0,
        )
    )

    result = scorer.score(
        make_layout_evaluation(
            total_cost=30.0,
            evaluated_weight=100.0,
        ),
        (
            make_finger_evaluation(
                penalty=0.1
            ),
        ),
        trigram_layout_evaluation=(
            make_trigram_layout_evaluation(
                total_cost=999.0,
                evaluated_weight=1.0,
            )
        ),
    )

    assert result.trigram_score == pytest.approx(
        999.0
    )

    assert (
        result.weighted_trigram_score
        == pytest.approx(0.0)
    )

    assert result.total == pytest.approx(
        1.0
    )


def test_zero_trigram_evaluated_weight_has_zero_score():
    scorer = CandidateScorer(
        CandidateScoreWeights(
            trigram_weight=5.0,
        )
    )

    result = scorer.score(
        make_layout_evaluation(),
        (),
        trigram_layout_evaluation=(
            make_trigram_layout_evaluation(
                total_cost=100.0,
                evaluated_weight=0.0,
            )
        ),
    )

    assert result.trigram_score == 0.0
    assert result.weighted_trigram_score == 0.0


def test_negative_trigram_weight_is_rejected():
    with pytest.raises(
        ValueError,
        match="trigram_weight must be non-negative",
    ):
        CandidateScoreWeights(
            trigram_weight=-1.0
        )