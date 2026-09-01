from __future__ import annotations

from dataclasses import dataclass
from random import Random
from statistics import mean

from evaluator.character_analyzer import CharacterAnalyzer
from evaluator.corpus_analyzer import CorpusAnalyzer
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry
from models.layout import Layout
from optimizer.local_search_optimizer import LocalSearchOptimizer
from tools.diagnose_multistart import (
    PROFILE,
    RANDOM_SEED,
    make_random_layout,
)
from tools.diagnose_simulated_annealing import (
    SA_STEPS,
    anneal,
)
from tools.diagnose_weight_sweep import (
    ROOT,
    load_text,
    make_evaluator,
    mapping_signature,
    raw_components,
)

BUDGET_PER_TRIAL = 25_000
TRIALS = 5
BUDGET_RANDOM_SEED = 20260904

SCORE_EPSILON = 1e-12

METHODS = (
    "A_random_local",
    "B_random_sa_local",
    "C_best_sa_local",
)


class CountingEvaluator:
    def __init__(self, evaluator) -> None:
        self._evaluator = evaluator
        self.count = 0

    def evaluate(self, *args, **kwargs):
        self.count += 1

        return self._evaluator.evaluate(
            *args,
            **kwargs,
        )


@dataclass(frozen=True)
class SearchResult:
    layout: Layout
    score: float
    transition: float
    trigram: float
    finger: float
    position: float
    evaluations: int
    source: str


def local_search_counted(
    layout: Layout,
    transition_statistics,
    character_statistics,
    trigram_statistics,
) -> SearchResult:
    counting_evaluator = CountingEvaluator(
        make_evaluator(PROFILE)
    )

    optimizer = LocalSearchOptimizer(
        candidate_evaluator=(
            counting_evaluator
        ),
    )

    result = optimizer.optimize(
        layout=layout,
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
            "Local search returned no score."
        )

    final_layout = (
        result.final_evaluation.layout
    )

    raw = raw_components(
        result.final_evaluation
    )

    return SearchResult(
        layout=final_layout,
        score=result.final_score,
        transition=raw["transition"],
        trigram=raw["trigram"],
        finger=raw["finger"],
        position=raw["position"],
        evaluations=counting_evaluator.count,
        source=(
            f"local(iter="
            f"{result.iteration_count})"
        ),
    )


def sa_then_local(
    start_layout: Layout,
    rng: Random,
    transition_statistics,
    character_statistics,
    trigram_statistics,
) -> SearchResult:
    sa_result = anneal(
        start_layout=start_layout,
        rng=rng,
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

    polished = local_search_counted(
        layout=sa_result["best_layout"],
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

    # anneal() evaluates the start once and
    # then one candidate for every SA step.
    sa_evaluations = SA_STEPS + 1

    return SearchResult(
        layout=polished.layout,
        score=polished.score,
        transition=polished.transition,
        trigram=polished.trigram,
        finger=polished.finger,
        position=polished.position,
        evaluations=(
            sa_evaluations
            + polished.evaluations
        ),
        source=(
            f"sa({SA_STEPS})+"
            f"{polished.source}"
        ),
    )


def make_known_best(
    physical_base: Layout,
    transition_statistics,
    character_statistics,
    trigram_statistics,
) -> SearchResult:
    rng = Random(RANDOM_SEED)

    random_01 = make_random_layout(
        base=physical_base,
        rng=rng,
        index=1,
    )

    return local_search_counted(
        layout=random_01,
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


def run_method_a(
    trial: int,
    physical_base: Layout,
    base_score: float,
    transition_statistics,
    character_statistics,
    trigram_statistics,
) -> dict[str, object]:
    rng = Random(
        BUDGET_RANDOM_SEED
        + trial * 10_000
        + 100
    )

    evaluations_used = 0
    starts_attempted = 0
    starts_accepted = 0

    accepted_results: list[
        SearchResult
    ] = []

    while True:
        starts_attempted += 1

        start = make_random_layout(
            base=physical_base,
            rng=rng,
            index=starts_attempted,
        )

        result = local_search_counted(
            layout=start,
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

        if (
            evaluations_used
            + result.evaluations
            > BUDGET_PER_TRIAL
        ):
            break

        evaluations_used += (
            result.evaluations
        )

        starts_accepted += 1
        accepted_results.append(result)

    if not accepted_results:
        raise RuntimeError(
            "Method A could not complete "
            "a single local search."
        )

    best = min(
        accepted_results,
        key=lambda item: item.score,
    )

    return {
        "method": METHODS[0],
        "trial": trial,
        "best": best,
        "evaluations": evaluations_used,
        "units": starts_accepted,
        "better": (
            best.score
            < base_score - SCORE_EPSILON
        ),
        "unique": len(
            {
                mapping_signature(
                    item.layout
                )
                for item
                in accepted_results
            }
        ),
    }


def run_method_b(
    trial: int,
    physical_base: Layout,
    base_score: float,
    transition_statistics,
    character_statistics,
    trigram_statistics,
) -> dict[str, object]:
    rng = Random(
        BUDGET_RANDOM_SEED
        + trial * 10_000
        + 200
    )

    evaluations_used = 0
    units_attempted = 0
    units_accepted = 0

    accepted_results: list[
        SearchResult
    ] = []

    while True:
        units_attempted += 1

        start = make_random_layout(
            base=physical_base,
            rng=rng,
            index=units_attempted,
        )

        result = sa_then_local(
            start_layout=start,
            rng=rng,
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

        if (
            evaluations_used
            + result.evaluations
            > BUDGET_PER_TRIAL
        ):
            break

        evaluations_used += (
            result.evaluations
        )

        units_accepted += 1
        accepted_results.append(result)

    if not accepted_results:
        raise RuntimeError(
            "Method B could not complete "
            "a single SA + LocalSearch unit."
        )

    best = min(
        accepted_results,
        key=lambda item: item.score,
    )

    return {
        "method": METHODS[1],
        "trial": trial,
        "best": best,
        "evaluations": evaluations_used,
        "units": units_accepted,
        "better": (
            best.score
            < base_score - SCORE_EPSILON
        ),
        "unique": len(
            {
                mapping_signature(
                    item.layout
                )
                for item
                in accepted_results
            }
        ),
    }


def run_method_c(
    trial: int,
    known_best: SearchResult,
    base_score: float,
    transition_statistics,
    character_statistics,
    trigram_statistics,
) -> dict[str, object]:
    rng = Random(
        BUDGET_RANDOM_SEED
        + trial * 10_000
        + 300
    )

    evaluations_used = 0
    units_accepted = 0

    accepted_results: list[
        SearchResult
    ] = []

    while True:
        result = sa_then_local(
            start_layout=known_best.layout,
            rng=rng,
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

        if (
            evaluations_used
            + result.evaluations
            > BUDGET_PER_TRIAL
        ):
            break

        evaluations_used += (
            result.evaluations
        )

        units_accepted += 1
        accepted_results.append(result)

    if not accepted_results:
        raise RuntimeError(
            "Method C could not complete "
            "a single SA + LocalSearch unit."
        )

    best = min(
        accepted_results,
        key=lambda item: item.score,
    )

    return {
        "method": METHODS[2],
        "trial": trial,
        "best": best,
        "evaluations": evaluations_used,
        "units": units_accepted,
        "better": (
            best.score
            < base_score - SCORE_EPSILON
        ),
        "unique": len(
            {
                mapping_signature(
                    item.layout
                )
                for item
                in accepted_results
            }
        ),
    }


def print_trial_result(
    row: dict[str, object],
) -> None:
    best = row["best"]

    if not isinstance(
        best,
        SearchResult,
    ):
        raise TypeError(
            "Expected SearchResult."
        )

    print(
        f"{row['method']!s:20}"
        f" trial={int(row['trial']):02d}"
        f" eval={int(row['evaluations']):6d}"
        f" units={int(row['units']):2d}"
        f" unique={int(row['unique']):2d}"
        f" best={best.score:10.6f}"
        f" better={bool(row['better'])}"
    )


def main() -> None:
    print(
        "Search-budget diagnostic"
        f"  profile={PROFILE.name}"
        f"  weights="
        f"{PROFILE.transition:g}/"
        f"{PROFILE.trigram:g}/"
        f"{PROFILE.finger:g}/"
        f"{PROFILE.position:g}"
    )

    print(
        f"budget_per_trial="
        f"{BUDGET_PER_TRIAL}"
        f" trials={TRIALS}"
        f" sa_steps={SA_STEPS}"
    )

    corpus = Corpus(
        entries=(
            CorpusEntry(load_text()),
        )
    )

    corpus_analyzer = CorpusAnalyzer()

    transition_statistics = (
        corpus_analyzer.analyze(corpus)
    )

    trigram_statistics = (
        corpus_analyzer.analyze_trigrams(
            corpus
        )
    )

    character_statistics = (
        CharacterAnalyzer().analyze(corpus)
    )

    physical_base = Layout.load(
        ROOT
        / "config/layouts"
        / "harmonia_v5_1b.json"
    )

    known_best = make_known_best(
        physical_base=physical_base,
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

    base_score = known_best.score

    print()
    print("=" * 110)
    print("KNOWN BEST BASELINE")
    print("=" * 110)

    print(
        f"score={known_best.score:.9f}"
        f" T={known_best.transition:.6f}"
        f" Tri={known_best.trigram:.6f}"
        f" F={known_best.finger:.6f}"
        f" P={known_best.position:.6f}"
        f" local_evaluations="
        f"{known_best.evaluations}"
    )

    rows: list[
        dict[str, object]
    ] = []

    print()
    print("=" * 110)
    print("TRIAL RESULTS")
    print("=" * 110)

    for trial in range(
        1,
        TRIALS + 1,
    ):
        row_a = run_method_a(
            trial=trial,
            physical_base=physical_base,
            base_score=base_score,
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

        row_b = run_method_b(
            trial=trial,
            physical_base=physical_base,
            base_score=base_score,
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

        row_c = run_method_c(
            trial=trial,
            known_best=known_best,
            base_score=base_score,
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

        rows.extend(
            (
                row_a,
                row_b,
                row_c,
            )
        )

        print_trial_result(row_a)
        print_trial_result(row_b)
        print_trial_result(row_c)
        print()

    print()
    print("=" * 110)
    print("METHOD SUMMARY")
    print("=" * 110)

    for method in METHODS:
        method_rows = [
            row
            for row in rows
            if row["method"] == method
        ]

        best_results: list[
            SearchResult
        ] = []

        for row in method_rows:
            item = row["best"]

            if not isinstance(
                item,
                SearchResult,
            ):
                raise TypeError(
                    "Expected SearchResult."
                )

            best_results.append(item)

        overall_best = min(
            best_results,
            key=lambda item: item.score,
        )

        success_count = sum(
            bool(row["better"])
            for row in method_rows
        )

        mean_score = mean(
            item.score
            for item in best_results
        )

        mean_evaluations = mean(
            int(row["evaluations"])
            for row in method_rows
        )

        mean_units = mean(
            int(row["units"])
            for row in method_rows
        )

        print(
            f"{method:20}"
            f" success="
            f"{success_count}/{TRIALS}"
            f" best="
            f"{overall_best.score:10.6f}"
            f" mean="
            f"{mean_score:10.6f}"
            f" mean_eval="
            f"{mean_evaluations:8.1f}"
            f" mean_units="
            f"{mean_units:5.2f}"
        )

    all_best: list[
        tuple[str, SearchResult]
    ] = []

    for row in rows:
        result = row["best"]

        if not isinstance(
            result,
            SearchResult,
        ):
            raise TypeError(
                "Expected SearchResult."
            )

        all_best.append(
            (
                str(row["method"]),
                result,
            )
        )

    best_method, best_result = min(
        all_best,
        key=lambda pair: pair[1].score,
    )

    print()
    print("=" * 110)
    print("BEST RESULT ACROSS ALL METHODS")
    print("=" * 110)

    print(
        f"method={best_method}"
    )

    print(
        f"score={best_result.score:.9f}"
        f" improvement_over_known_best="
        f"{base_score - best_result.score:.9f}"
    )

    print(
        f"T={best_result.transition:.6f}"
        f" Tri={best_result.trigram:.6f}"
        f" F={best_result.finger:.6f}"
        f" P={best_result.position:.6f}"
    )

    print()
    print(
        mapping_signature(
            best_result.layout
        )
    )


if __name__ == "__main__":
    main()
