from __future__ import annotations

from app.optimization_app import OptimizationApp
from config_loader.constraint_config_loader import (
    ConstraintConfigLoader,
)
from config_loader.optimization_config_loader import (
    OptimizationConfigLoader,
)
from config_loader.search_budget_profiles_loader import (
    SearchBudgetProfilesLoader,
)
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry
from models.layout import Layout
from models.multi_start_optimization_result import (
    MultiStartOptimizationResult,
)
from models.search_mode import SearchMode


def test_default_fast_optimization_pipeline() -> None:
    optimization_config = (
        OptimizationConfigLoader.load(
            "config/optimization/default.json"
        )
    )

    constraint_config = (
        ConstraintConfigLoader.load(
            "config/constraints/default.json"
        )
    )

    search_profiles = (
        SearchBudgetProfilesLoader.load(
            "config/search/default.json"
        )
    )

    layout = Layout.load(
        "config/layouts/harmonia_v5_1b.json"
    )

    corpus = Corpus(
        entries=(
            CorpusEntry(
                "harmonia keyboard layout "
                "typescript python rust "
                "konnichiwa watashi"
            ),
        )
    )

    app = OptimizationApp(
        config=optimization_config,
        constraint_config=constraint_config,
    )

    result = app.optimize_with_mode(
        layout=layout,
        corpus=corpus,
        mode=SearchMode.FAST,
        profiles=search_profiles,
        seed=20260909,
    )

    assert isinstance(
        result,
        MultiStartOptimizationResult,
    )

    assert (
        result.run_count
        == search_profiles.fast.runs
    )

    assert result.best_result is not None
    assert result.best_score is not None

    best = result.best_result

    assert best.final_score is not None
    assert (
        best.final_evaluation.is_valid
        is True
    )
