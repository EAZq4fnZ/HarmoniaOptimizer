from __future__ import annotations

from statistics import mean, median
from time import perf_counter

from evaluator.character_analyzer import CharacterAnalyzer
from evaluator.corpus_analyzer import CorpusAnalyzer
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry
from models.layout import Layout
from optimizer.local_search_optimizer import LocalSearchOptimizer
from optimizer.random_start_layout_factory import (
    RandomStartLayoutFactory,
)
from tools.diagnose_multistart import PROFILE
from tools.diagnose_weight_sweep import (
    ROOT,
    load_text,
    make_evaluator,
)

RUN_VALUES = (
    1,
    2,
    4,
    8,
    16,
)

TRIALS = 5
MAX_ITERATIONS = 30
BASE_SEED = 20260906


def run_trial(
    base_layout: Layout,
    runs: int,
    trial: int,
    transition_statistics,
    character_statistics,
    trigram_statistics,
) -> tuple[float, float]:
    factory = RandomStartLayoutFactory(
        seed=BASE_SEED + trial
    )

    scores: list[float] = []

    started = perf_counter()

    for run_index in range(runs):
        start_layout = factory.create(
            base_layout=base_layout,
            run_index=run_index,
        )

        optimizer = LocalSearchOptimizer(
            candidate_evaluator=make_evaluator(
                PROFILE
            ),
            max_iterations=MAX_ITERATIONS,
        )

        result = optimizer.optimize(
            layout=start_layout,
            transition_statistics=(
                transition_statistics
            ),
            character_statistics=(
                character_statistics
            ),
            trigram_statistics=(
                trigram_statistics
            ),
        )

        if result.final_score is None:
            raise RuntimeError(
                "Optimization returned "
                "no final score."
            )

        scores.append(
            result.final_score
        )

    elapsed = perf_counter() - started

    return min(scores), elapsed


def main() -> None:
    print(
        "Multi-start run-count benchmark"
        f"  profile={PROFILE.name}"
    )
    print(
        f"trials={TRIALS}"
        f" max_iterations={MAX_ITERATIONS}"
        f" base_seed={BASE_SEED}"
    )
    print()

    corpus = Corpus(
        entries=(
            CorpusEntry(
                load_text()
            ),
        )
    )

    corpus_analyzer = CorpusAnalyzer()

    transition_statistics = (
        corpus_analyzer.analyze(
            corpus
        )
    )

    trigram_statistics = (
        corpus_analyzer.analyze_trigrams(
            corpus
        )
    )

    character_statistics = (
        CharacterAnalyzer().analyze(
            corpus
        )
    )

    base_layout = Layout.load(
        ROOT
        / "config/layouts"
        / "harmonia_v5_1b.json"
    )

    print(
        "runs  mean_best  median_best"
        "   best_best   worst_best"
        "   mean_time_s"
    )
    print("-" * 76)

    for runs in RUN_VALUES:
        best_scores: list[float] = []
        elapsed_values: list[float] = []

        for trial in range(TRIALS):
            best_score, elapsed = run_trial(
                base_layout=base_layout,
                runs=runs,
                trial=trial,
                transition_statistics=(
                    transition_statistics
                ),
                character_statistics=(
                    character_statistics
                ),
                trigram_statistics=(
                    trigram_statistics
                ),
            )

            best_scores.append(
                best_score
            )
            elapsed_values.append(
                elapsed
            )

        print(
            f"{runs:4d}"
            f"  {mean(best_scores):9.6f}"
            f"  {median(best_scores):11.6f}"
            f"  {min(best_scores):10.6f}"
            f"  {max(best_scores):11.6f}"
            f"  {mean(elapsed_values):11.3f}"
        )


if __name__ == "__main__":
    main()
