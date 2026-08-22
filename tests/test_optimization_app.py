# tests/test_optimization_app.py

import pytest

from app.optimization_app import OptimizationApp
from models.candidate_score import CandidateScoreWeights
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry
from models.enums import Finger, Hand
from models.finger_load_budget import FingerLoadBudget
from models.layout import Layout
from models.optimization_config import OptimizationConfig
from models.optimization_result import OptimizationResult
from models.transition_cost import TransitionCostWeights


def make_layout() -> Layout:
    return Layout(
        name="Optimization App Test",
        version="0.1.0",
        layer="L0",
        description="Optimization application test layout",
        mapping={
            "A": "L-I-H-3",
            "B": "R-I-H-3",
            "C": "L-R-H-1",
            "D": "L-M-T-2",
            "E": "L-M-H-2",
            "F": "L-I-T-3",
            "G": "L-I-H-4",
            "H": "L-I-T-4",
            "I": "R-I-T-3",
            "J": "R-I-H-4",
            "K": "R-I-T-4",
            "L": "R-M-H-2",
            "M": "R-R-H-1",
            "N": "R-M-T-2",
            "O": "R-M-B-2",
            "P": "R-R-T-1",
            "Q": "L-P-H-0",
            "R": "L-R-T-1",
            "S": "L-M-B-2",
            "T": "L-I-B-3",
            "U": "R-R-B-1",
            "V": "R-I-B-3",
            "W": "R-P-H-0",
            "X": "L-P-T-0",
            "Y": "L-P-B-0",
            "Z": "R-P-T-0",
        },
    )


def make_corpus() -> Corpus:
    return Corpus(
        entries=(
            CorpusEntry(
                text=(
                    "THE QUICK BROWN FOX JUMPS "
                    "OVER THE LAZY DOG"
                ),
            ),
        ),
    )


def make_config() -> OptimizationConfig:
    return OptimizationConfig(
        version="1.0",
        transition_cost_weights=TransitionCostWeights(
            same_finger_penalty=10.0,
            same_hand_penalty=2.0,
            row_change_penalty=1.5,
            alternation_reward=2.0,
            inward_roll_reward=1.5,
            outward_roll_reward=0.5,
        ),
        candidate_score_weights=CandidateScoreWeights(
            transition_weight=1.0,
            finger_load_weight=1.0,
        ),
        finger_load_budgets=(
            FingerLoadBudget(
                hand=Hand.LEFT,
                finger=Finger.INDEX,
                target_ratio=0.25,
                tolerance=0.05,
            ),
            FingerLoadBudget(
                hand=Hand.LEFT,
                finger=Finger.MIDDLE,
                target_ratio=0.15,
                tolerance=0.05,
            ),
            FingerLoadBudget(
                hand=Hand.LEFT,
                finger=Finger.RING,
                target_ratio=0.07,
                tolerance=0.03,
            ),
            FingerLoadBudget(
                hand=Hand.LEFT,
                finger=Finger.PINKY,
                target_ratio=0.03,
                tolerance=0.02,
            ),
            FingerLoadBudget(
                hand=Hand.RIGHT,
                finger=Finger.INDEX,
                target_ratio=0.25,
                tolerance=0.05,
            ),
            FingerLoadBudget(
                hand=Hand.RIGHT,
                finger=Finger.MIDDLE,
                target_ratio=0.15,
                tolerance=0.05,
            ),
            FingerLoadBudget(
                hand=Hand.RIGHT,
                finger=Finger.RING,
                target_ratio=0.07,
                tolerance=0.03,
            ),
            FingerLoadBudget(
                hand=Hand.RIGHT,
                finger=Finger.PINKY,
                target_ratio=0.03,
                tolerance=0.02,
            ),
        ),
    )


def make_app(
    max_iterations: int = 1,
) -> OptimizationApp:
    return OptimizationApp(
        config=make_config(),
        max_iterations=max_iterations,
    )


def test_app_max_iterations():
    app = make_app(
        max_iterations=3,
    )

    assert app.max_iterations == 3


def test_app_preserves_config():
    config = make_config()

    app = OptimizationApp(
        config=config,
        max_iterations=1,
    )

    assert app.config is config


def test_app_rejects_negative_max_iterations():
    with pytest.raises(ValueError):
        OptimizationApp(
            config=make_config(),
            max_iterations=-1,
        )


def test_app_returns_optimization_result():
    app = make_app()

    result = app.optimize(
        layout=make_layout(),
        corpus=make_corpus(),
    )

    assert isinstance(
        result,
        OptimizationResult,
    )


def test_app_result_is_valid():
    app = make_app()

    result = app.optimize(
        layout=make_layout(),
        corpus=make_corpus(),
    )

    assert result.initial_evaluation.is_valid is True
    assert result.final_evaluation.is_valid is True


def test_app_does_not_worsen_score():
    app = make_app()

    result = app.optimize(
        layout=make_layout(),
        corpus=make_corpus(),
    )

    assert result.initial_score is not None
    assert result.final_score is not None

    assert (
        result.final_score
        <= result.initial_score
    )


def test_optimize_text():
    app = make_app()

    result = app.optimize_text(
        layout=make_layout(),
        text="HELLO WORLD",
    )

    assert isinstance(
        result,
        OptimizationResult,
    )

    assert result.final_score is not None


def test_format_result():
    app = make_app(
        max_iterations=0,
    )

    result = app.optimize(
        layout=make_layout(),
        corpus=make_corpus(),
    )

    report = app.format_result(
        result
    )

    assert isinstance(report, str)
    assert "Optimization Result" in report
    assert "Initial score:" in report
    assert "Final score:" in report