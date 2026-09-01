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
    8,
    16,
    32,
)

TRIALS = 3
MAX_ITERATIONS = 30
BASE_SEED = 20260907


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
                "Optimization returned no final score."
            )

        scores.append(
            result.final_score
        )

    return (
        min(scores),
        perf_counter() - started,
    )


def main() -> None:
    corpus = Corpus(
        entries=(
            CorpusEntry(
                load_text()
            ),
        )
    )

    analyzer = CorpusAnalyzer()

    transition_statistics = analyzer.analyze(
        corpus
    )

    trigram_statistics = (
        analyzer.analyze_trigrams(
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
        "Deep-budget benchmark"
        f"  trials={TRIALS}"
        f" max_iterations={MAX_ITERATIONS}"
    )
    print()
    print(
        "runs  mean_best  median_best"
        "   best_best   worst_best"
        "   mean_time_s"
    )
    print("-" * 76)

    for runs in RUN_VALUES:
        scores: list[float] = []
        times: list[float] = []

        for trial in range(TRIALS):
            score, elapsed = run_trial(
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

            scores.append(score)
            times.append(elapsed)

        print(
            f"{runs:4d}"
            f"  {mean(scores):9.6f}"
            f"  {median(scores):11.6f}"
            f"  {min(scores):10.6f}"
            f"  {max(scores):11.6f}"
            f"  {mean(times):11.3f}"
        )


if __name__ == "__main__":
    main()
