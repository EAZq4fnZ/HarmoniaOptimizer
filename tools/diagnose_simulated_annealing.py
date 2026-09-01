from __future__ import annotations

import math
from random import Random
from statistics import mean

from evaluator.character_analyzer import CharacterAnalyzer
from evaluator.corpus_analyzer import CorpusAnalyzer
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry
from models.layout import Layout
from optimizer.layout_mutator import LayoutMutator
from optimizer.local_search_optimizer import LocalSearchOptimizer
from tools.diagnose_multistart import (
    PROFILE,
    RANDOM_SEED,
    make_random_layout,
)
from tools.diagnose_weight_sweep import (
    ROOT,
    load_text,
    make_evaluator,
    mapping_signature,
    raw_components,
)

T_INITIAL = 1.647152287
T_FINAL = 0.079812775

SA_STEPS = 5_000
SA_RUNS = 10
SA_RANDOM_SEED = 20260903

SCORE_EPSILON = 1e-12


def temperature_at_step(
    step: int,
    total_steps: int,
) -> float:
    if total_steps < 2:
        return T_FINAL

    progress = step / (
        total_steps - 1
    )

    return T_INITIAL * (
        T_FINAL / T_INITIAL
    ) ** progress


def optimize_locally(
    layout: Layout,
    transition_statistics,
    character_statistics,
    trigram_statistics,
):
    evaluator = make_evaluator(PROFILE)

    optimizer = LocalSearchOptimizer(
        candidate_evaluator=evaluator,
    )

    return optimizer.optimize(
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


def evaluate_layout(
    layout: Layout,
    evaluator,
    transition_statistics,
    character_statistics,
    trigram_statistics,
):
    evaluation = evaluator.evaluate(
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

    if evaluation.score is None:
        raise RuntimeError(
            "Candidate evaluation has no score."
        )

    return evaluation


def anneal(
    start_layout: Layout,
    rng: Random,
    transition_statistics,
    character_statistics,
    trigram_statistics,
):
    evaluator = make_evaluator(PROFILE)
    mutator = LayoutMutator()

    current_evaluation = evaluate_layout(
        layout=start_layout,
        evaluator=evaluator,
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

    current_layout = start_layout
    current_score = current_evaluation.score

    if current_score is None:
        raise RuntimeError(
            "Initial evaluation has no score."
        )

    best_layout = current_layout
    best_evaluation = current_evaluation
    best_score = current_score

    letters = sorted(
        start_layout.mapping
    )

    accepted = 0
    accepted_worse = 0
    rejected = 0
    improving_moves = 0
    neutral_moves = 0
    worsening_moves = 0
    best_updates = 0

    for step in range(SA_STEPS):
        temperature = temperature_at_step(
            step=step,
            total_steps=SA_STEPS,
        )

        first_letter, second_letter = (
            rng.sample(
                letters,
                2,
            )
        )

        candidate_layout = mutator.swap(
            layout=current_layout,
            letter1=first_letter,
            letter2=second_letter,
        )

        candidate_evaluation = (
            evaluate_layout(
                layout=candidate_layout,
                evaluator=evaluator,
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
        )

        candidate_score = (
            candidate_evaluation.score
        )

        if candidate_score is None:
            raise RuntimeError(
                "Candidate score is None."
            )

        delta = (
            candidate_score
            - current_score
        )

        if delta < -SCORE_EPSILON:
            improving_moves += 1
            accept = True
        elif delta > SCORE_EPSILON:
            worsening_moves += 1

            probability = math.exp(
                -delta / temperature
            )

            accept = (
                rng.random()
                < probability
            )
        else:
            neutral_moves += 1
            accept = True

        if accept:
            if delta > SCORE_EPSILON:
                accepted_worse += 1

            accepted += 1

            current_layout = (
                candidate_layout
            )
            current_evaluation = (
                candidate_evaluation
            )
            current_score = (
                candidate_score
            )
        else:
            rejected += 1

        if (
            candidate_score
            < best_score - SCORE_EPSILON
        ):
            best_layout = (
                candidate_layout
            )
            best_evaluation = (
                candidate_evaluation
            )
            best_score = (
                candidate_score
            )
            best_updates += 1

    return {
        "best_layout": best_layout,
        "best_evaluation": best_evaluation,
        "best_score": best_score,
        "final_layout": current_layout,
        "final_score": current_score,
        "accepted": accepted,
        "accepted_worse": accepted_worse,
        "rejected": rejected,
        "improving_moves": improving_moves,
        "neutral_moves": neutral_moves,
        "worsening_moves": worsening_moves,
        "best_updates": best_updates,
    }


def main() -> None:
    print(
        "Simulated annealing diagnostic"
        f"  profile={PROFILE.name}"
        f"  weights="
        f"{PROFILE.transition:g}/"
        f"{PROFILE.trigram:g}/"
        f"{PROFILE.finger:g}/"
        f"{PROFILE.position:g}"
    )

    print(
        f"runs={SA_RUNS}"
        f" steps={SA_STEPS}"
        f" T_initial={T_INITIAL:.9f}"
        f" T_final={T_FINAL:.9f}"
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

    start_rng = Random(RANDOM_SEED)

    random_01 = make_random_layout(
        base=physical_base,
        rng=start_rng,
        index=1,
    )

    base_result = optimize_locally(
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

    if base_result.final_score is None:
        raise RuntimeError(
            "Base local optimum has no score."
        )

    base_layout = (
        base_result.final_evaluation.layout
    )

    base_score = (
        base_result.final_score
    )

    base_raw = raw_components(
        base_result.final_evaluation
    )

    print()
    print("=" * 110)
    print("BASE LOCAL OPTIMUM")
    print("=" * 110)

    print(
        f"total={base_score:.9f}"
        f" T={base_raw['transition']:.6f}"
        f" Tri={base_raw['trigram']:.6f}"
        f" F={base_raw['finger']:.6f}"
        f" P={base_raw['position']:.6f}"
    )

    rows: list[dict[str, object]] = []

    for run in range(
        1,
        SA_RUNS + 1,
    ):
        rng = Random(
            SA_RANDOM_SEED + run
        )

        sa_result = anneal(
            start_layout=base_layout,
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

        polished_result = (
            optimize_locally(
                layout=sa_result[
                    "best_layout"
                ],
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
        )

        if polished_result.final_score is None:
            raise RuntimeError(
                "Polished result has no score."
            )

        polished_raw = raw_components(
            polished_result.final_evaluation
        )

        improvement = (
            base_score
            - polished_result.final_score
        )

        row: dict[str, object] = {
            "run": run,
            "sa_best": float(
                sa_result["best_score"]
            ),
            "sa_final": float(
                sa_result["final_score"]
            ),
            "polished": (
                polished_result.final_score
            ),
            "improvement": improvement,
            "transition": (
                polished_raw["transition"]
            ),
            "trigram": (
                polished_raw["trigram"]
            ),
            "finger": (
                polished_raw["finger"]
            ),
            "position": (
                polished_raw["position"]
            ),
            "accepted": int(
                sa_result["accepted"]
            ),
            "accepted_worse": int(
                sa_result["accepted_worse"]
            ),
            "rejected": int(
                sa_result["rejected"]
            ),
            "best_updates": int(
                sa_result["best_updates"]
            ),
            "signature": mapping_signature(
                polished_result
                .final_evaluation
                .layout
            ),
            "layout": (
                polished_result
                .final_evaluation
                .layout
            ),
        }

        rows.append(row)

        print(
            f"run={run:02d}"
            f" sa_best="
            f"{float(sa_result['best_score']):9.4f}"
            f" sa_final="
            f"{float(sa_result['final_score']):9.4f}"
            f" polished="
            f"{polished_result.final_score:9.4f}"
            f" improvement="
            f"{improvement:+9.4f}"
            f" accepted="
            f"{int(sa_result['accepted']):4d}"
            f" worse="
            f"{int(sa_result['accepted_worse']):4d}"
            f" best_updates="
            f"{int(sa_result['best_updates']):3d}"
        )

    best = min(
        rows,
        key=lambda row: float(
            row["polished"]
        ),
    )

    unique_signatures = {
        str(row["signature"])
        for row in rows
    }

    better_rows = [
        row
        for row in rows
        if float(row["polished"])
        < base_score - SCORE_EPSILON
    ]

    print()
    print("=" * 110)
    print("SUMMARY")
    print("=" * 110)

    print(
        f"runs                  : "
        f"{len(rows)}"
    )
    print(
        f"better than base      : "
        f"{len(better_rows)}/{len(rows)}"
    )
    print(
        f"unique polished layouts: "
        f"{len(unique_signatures)}"
    )
    print(
        f"mean polished score   : "
        f"{mean(float(row['polished']) for row in rows):.9f}"
    )
    print(
        f"best polished score   : "
        f"{float(best['polished']):.9f}"
    )
    print(
        f"best improvement      : "
        f"{float(best['improvement']):.9f}"
    )

    print()
    print("BEST POLISHED RESULT")
    print("-" * 110)

    print(
        f"run={int(best['run']):02d}"
    )
    print(
        f"T={float(best['transition']):.6f}"
        f" Tri={float(best['trigram']):.6f}"
        f" F={float(best['finger']):.6f}"
        f" P={float(best['position']):.6f}"
    )

    print()
    print(
        mapping_signature(
            best["layout"]
        )
    )


if __name__ == "__main__":
    main()
