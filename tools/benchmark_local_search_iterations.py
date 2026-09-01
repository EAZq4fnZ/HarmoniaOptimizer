from __future__ import annotations

from statistics import mean
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

MAX_ITERATION_VALUES = (
    5,
    10,
    15,
    20,
    30,
)

RUNS_PER_VALUE = 20
RANDOM_SEED = 20260905


def main() -> None:
    print(
        "Local-search iteration-budget benchmark"
        f"  profile={PROFILE.name}"
    )
    print(
        f"runs_per_value={RUNS_PER_VALUE}"
        f" seed={RANDOM_SEED}"
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

    start_factory = RandomStartLayoutFactory(
        seed=RANDOM_SEED
    )

    print(
        "max_iter  mean_steps  hit_limit"
        "  mean_score   best_score"
        "   elapsed_s"
    )
    print("-" * 78)

    for max_iterations in MAX_ITERATION_VALUES:
        scores: list[float] = []
        steps: list[int] = []

        hit_limit = 0

        started = perf_counter()

        for run_index in range(
            RUNS_PER_VALUE
        ):
            start_layout = (
                start_factory.create(
                    base_layout=base_layout,
                    run_index=run_index,
                )
            )

            optimizer = LocalSearchOptimizer(
                candidate_evaluator=(
                    make_evaluator(
                        PROFILE
                    )
                ),
                max_iterations=(
                    max_iterations
                ),
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

            steps.append(
                result.iteration_count
            )

            if (
                result.iteration_count
                == max_iterations
            ):
                hit_limit += 1

        elapsed = (
            perf_counter()
            - started
        )

        print(
            f"{max_iterations:8d}"
            f"  {mean(steps):10.2f}"
            f"  {hit_limit:9d}"
            f"  {mean(scores):10.6f}"
            f"  {min(scores):10.6f}"
            f"  {elapsed:10.3f}"
        )


if __name__ == "__main__":
    main()
