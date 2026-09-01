# tests/test_optimization_app.py

import pytest

from app.optimization_app import OptimizationApp
from models.candidate_score import CandidateScoreWeights
from models.constraint_config import (
    ConstraintConfig,
    ForbiddenPositionConstraintConfig,
    VowelHandDistributionConstraintConfig,
    VowelPositionConstraintConfig,
)
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry
from models.enums import Finger, Hand
from models.finger_load_budget import FingerLoadBudget
from models.layout import Layout
from models.optimization_config import OptimizationConfig
from models.optimization_result import OptimizationResult
from models.search_budget import SearchBudget
from models.search_budget_profiles import SearchBudgetProfiles
from models.search_mode import SearchMode
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
        constraint_config=make_constraint_config(),
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
        constraint_config=make_constraint_config(),
        max_iterations=1,
    )

    assert app.config is config


def test_app_preserves_constraint_config():
    constraint_config = make_constraint_config()

    app = OptimizationApp(
        config=make_config(),
        constraint_config=constraint_config,
        max_iterations=1,
    )

    assert app.constraint_config is constraint_config


def test_app_rejects_negative_max_iterations():
    with pytest.raises(ValueError):
        OptimizationApp(
            config=make_config(),
            constraint_config=make_constraint_config(),
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


def make_constraint_config() -> ConstraintConfig:
    return ConstraintConfig(
        version="1.0",
        vowel_position=VowelPositionConstraintConfig(
            enabled=False,
            allowed_positions=frozenset(),
        ),
        forbidden_position=ForbiddenPositionConstraintConfig(
            enabled=False,
            forbidden_positions=frozenset(),
        ),
    )
def test_optimize_multi_start_returns_multi_start_result():
    from models.multi_start_optimization_result import (
        MultiStartOptimizationResult,
    )

    app = make_app(
        max_iterations=0,
    )

    result = app.optimize_multi_start(
        layout=make_layout(),
        corpus=make_corpus(),
        runs=3,
        seed=12345,
    )

    assert isinstance(
        result,
        MultiStartOptimizationResult,
    )

    assert result.run_count == 3


def test_optimize_multi_start_has_best_result():
    app = make_app(
        max_iterations=0,
    )

    result = app.optimize_multi_start(
        layout=make_layout(),
        corpus=make_corpus(),
        runs=3,
        seed=12345,
    )

    assert result.best_result is not None
    assert result.best_score is not None


def test_optimize_multi_start_is_reproducible():
    app = make_app(
        max_iterations=0,
    )

    first = app.optimize_multi_start(
        layout=make_layout(),
        corpus=make_corpus(),
        runs=3,
        seed=12345,
    )

    second = app.optimize_multi_start(
        layout=make_layout(),
        corpus=make_corpus(),
        runs=3,
        seed=12345,
    )

    assert first.best_result is not None
    assert second.best_result is not None

    assert (
        first.best_result.final_evaluation.layout.mapping
        == second.best_result.final_evaluation.layout.mapping
    )

    assert (
        first.best_score
        == second.best_score
    )


def test_optimize_multi_start_rejects_zero_runs():
    app = make_app(
        max_iterations=0,
    )

    with pytest.raises(
        ValueError,
        match=(
            "runs must be greater than or equal to 1"
        ),
    ):
        app.optimize_multi_start(
            layout=make_layout(),
            corpus=make_corpus(),
            runs=0,
            seed=12345,
        )


def test_existing_optimize_still_returns_optimization_result():
    app = make_app(
        max_iterations=0,
    )

    result = app.optimize(
        layout=make_layout(),
        corpus=make_corpus(),
    )

    assert isinstance(
        result,
        OptimizationResult,
    )

def test_multi_start_uses_vowel_constrained_factory_when_vowel_enabled(
    monkeypatch,
):
    constraint_config = ConstraintConfig(
        version="1.0",
        vowel_position=VowelPositionConstraintConfig(
            enabled=True,
            allowed_positions=frozenset({
                "L-I-T-3",
                "L-M-H-2",
                "R-I-T-3",
                "R-M-H-2",
                "R-R-H-1",
            }),
        ),
        forbidden_position=ForbiddenPositionConstraintConfig(
            enabled=False,
            forbidden_positions=frozenset(),
        ),
    )

    app = OptimizationApp(
        config=make_config(),
        constraint_config=constraint_config,
        max_iterations=0,
    )

    created = []

    class FakeFactory:
        def __init__(
            self,
            config,
            seed,
        ):
            created.append(
                ("vowel", config, seed)
            )

        def create(
            self,
            base_layout,
            run_index,
        ):
            return base_layout

    monkeypatch.setattr(
        "app.optimization_app."
        "VowelConstrainedStartLayoutFactory",
        FakeFactory,
    )

    result = app.optimize_multi_start(
        layout=make_layout(),
        corpus=make_corpus(),
        runs=2,
        seed=12345,
    )

    assert result.run_count == 2
    assert len(created) == 1
    assert created[0][0] == "vowel"
    assert created[0][1] is app.constraint_config
    assert created[0][2] == 12345


def test_multi_start_uses_random_factory_when_vowel_constraints_disabled(
    monkeypatch,
):
    constraint_config = ConstraintConfig(
        version="1.0",
        vowel_position=VowelPositionConstraintConfig(
            enabled=False,
            allowed_positions=frozenset(),
        ),
        forbidden_position=ForbiddenPositionConstraintConfig(
            enabled=False,
            forbidden_positions=frozenset(),
        ),
    )

    app = OptimizationApp(
        config=make_config(),
        constraint_config=constraint_config,
        max_iterations=0,
    )

    created = []

    class FakeFactory:
        def __init__(
            self,
            seed,
        ):
            created.append(
                ("random", seed)
            )

        def create(
            self,
            base_layout,
            run_index,
        ):
            return base_layout

    monkeypatch.setattr(
        "app.optimization_app."
        "RandomStartLayoutFactory",
        FakeFactory,
    )

    result = app.optimize_multi_start(
        layout=make_layout(),
        corpus=make_corpus(),
        runs=2,
        seed=12345,
    )

    assert result.run_count == 2
    assert created == [
        ("random", 12345)
    ]

def test_multi_start_uses_vowel_constrained_factory_when_hand_distribution_enabled(
    monkeypatch,
):
    constraint_config = ConstraintConfig(
        version="1.0",
        vowel_position=VowelPositionConstraintConfig(
            enabled=False,
            allowed_positions=frozenset(),
        ),
        forbidden_position=ForbiddenPositionConstraintConfig(
            enabled=False,
            forbidden_positions=frozenset(),
        ),
        vowel_hand_distribution=VowelHandDistributionConstraintConfig(
            enabled=True,
            min_left_vowels=2,
            max_left_vowels=3,
        ),
    )

    app = OptimizationApp(
        config=make_config(),
        constraint_config=constraint_config,
        max_iterations=0,
    )

    created = []

    class FakeFactory:
        def __init__(
            self,
            config,
            seed,
        ):
            created.append(
                ("vowel", config, seed)
            )

        def create(
            self,
            base_layout,
            run_index,
        ):
            return base_layout

    monkeypatch.setattr(
        "app.optimization_app."
        "VowelConstrainedStartLayoutFactory",
        FakeFactory,
    )

    result = app.optimize_multi_start(
        layout=make_layout(),
        corpus=make_corpus(),
        runs=2,
        seed=12345,
    )

    assert result.run_count == 2
    assert created == [
        (
            "vowel",
            app.constraint_config,
            12345,
        )
    ]

def test_optimize_with_budget_uses_budget_values(
    monkeypatch,
):
    app = make_app(
        max_iterations=999,
    )

    captured = {}
    sentinel = object()

    def fake_optimize_multi_start(
        self,
        layout,
        corpus,
        runs,
        seed,
    ):
        captured["app"] = self
        captured["layout"] = layout
        captured["corpus"] = corpus
        captured["runs"] = runs
        captured["seed"] = seed
        captured["max_iterations"] = (
            self._max_iterations
        )

        return sentinel

    monkeypatch.setattr(
        OptimizationApp,
        "optimize_multi_start",
        fake_optimize_multi_start,
    )

    layout = make_layout()
    corpus = make_corpus()

    budget = SearchBudget(
        runs=7,
        max_iterations=12,
    )

    result = app.optimize_with_budget(
        layout=layout,
        corpus=corpus,
        budget=budget,
        seed=12345,
    )

    assert result is sentinel
    assert captured["app"] is not app
    assert captured["layout"] is layout
    assert captured["corpus"] is corpus
    assert captured["runs"] == 7
    assert captured["seed"] == 12345
    assert captured["max_iterations"] == 12


def test_optimize_with_mode_uses_profile_budget(
    monkeypatch,
):
    app = make_app(
        max_iterations=999,
    )

    profiles = SearchBudgetProfiles(
        fast=SearchBudget(
            runs=2,
            max_iterations=10,
        ),
        standard=SearchBudget(
            runs=5,
            max_iterations=20,
        ),
        deep=SearchBudget(
            runs=10,
            max_iterations=30,
        ),
    )

    captured = {}
    sentinel = object()

    def fake_optimize_with_budget(
        self,
        layout,
        corpus,
        budget,
        seed,
    ):
        captured["self"] = self
        captured["layout"] = layout
        captured["corpus"] = corpus
        captured["budget"] = budget
        captured["seed"] = seed

        return sentinel

    monkeypatch.setattr(
        OptimizationApp,
        "optimize_with_budget",
        fake_optimize_with_budget,
    )

    layout = make_layout()
    corpus = make_corpus()

    result = app.optimize_with_mode(
        layout=layout,
        corpus=corpus,
        mode=SearchMode.STANDARD,
        profiles=profiles,
        seed=12345,
    )

    assert result is sentinel
    assert captured["self"] is app
    assert captured["layout"] is layout
    assert captured["corpus"] is corpus
    assert captured["budget"] == profiles.standard
    assert captured["seed"] == 12345
