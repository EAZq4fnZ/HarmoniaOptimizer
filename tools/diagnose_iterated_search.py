from __future__ import annotations

from collections import defaultdict
from random import Random

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
    pareto_frontier,
)
from tools.diagnose_weight_sweep import (
    ROOT,
    dominates,
    load_text,
    make_evaluator,
    mapping_signature,
    raw_components,
)

PERTURBATION_STRENGTHS = (2, 3, 4)
TRIALS_PER_STRENGTH = 20
PERTURBATION_SEED = 20260902


def optimize_layout(
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
        transition_statistics=transition_statistics,
        character_statistics=character_statistics,
        trigram_statistics=trigram_statistics,
    )


def perturb_layout(
    layout: Layout,
    strength: int,
    rng: Random,
) -> Layout:
    if strength < 1:
        raise ValueError(
            "strength must be at least 1"
        )

    letters = sorted(layout.mapping)

    required_letters = strength * 2

    if required_letters > len(letters):
        raise ValueError(
            "perturbation strength is too large"
        )

    selected = rng.sample(
        letters,
        required_letters,
    )

    mutator = LayoutMutator()
    perturbed = layout

    for index in range(
        0,
        required_letters,
        2,
    ):
        perturbed = mutator.swap(
            layout=perturbed,
            letter1=selected[index],
            letter2=selected[index + 1],
        )

    return perturbed


def main() -> None:
    print(
        "Iterated local search diagnostic"
        f"  profile={PROFILE.name}"
        f"  weights="
        f"{PROFILE.transition:g}/"
        f"{PROFILE.trigram:g}/"
        f"{PROFILE.finger:g}/"
        f"{PROFILE.position:g}"
    )

    print(
        f"base_random_seed={RANDOM_SEED}"
        f" perturbation_seed={PERTURBATION_SEED}"
    )

    print(
        f"strengths={PERTURBATION_STRENGTHS}"
        f" trials_per_strength={TRIALS_PER_STRENGTH}"
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

    base_result = optimize_layout(
        layout=random_01,
        transition_statistics=transition_statistics,
        character_statistics=character_statistics,
        trigram_statistics=trigram_statistics,
    )

    if base_result.final_score is None:
        raise RuntimeError(
            "Base local optimum has no score."
        )

    base_layout = (
        base_result.final_evaluation.layout
    )

    base_raw = raw_components(
        base_result.final_evaluation
    )

    base_signature = mapping_signature(
        base_layout
    )

    base_score = base_result.final_score

    print()
    print("=" * 110)
    print("BASE LOCAL OPTIMUM")
    print("=" * 110)

    print(
        f"iterations={base_result.iteration_count}"
        f" total={base_score:.6f}"
        f" T={base_raw['transition']:.6f}"
        f" Tri={base_raw['trigram']:.6f}"
        f" F={base_raw['finger']:.6f}"
        f" P={base_raw['position']:.6f}"
    )

    rows: list[dict[str, object]] = []

    perturb_rng = Random(
        PERTURBATION_SEED
    )

    for strength in PERTURBATION_STRENGTHS:
        print()
        print("=" * 110)
        print(
            f"PERTURBATION STRENGTH {strength}"
        )
        print("=" * 110)

        for trial in range(
            1,
            TRIALS_PER_STRENGTH + 1,
        ):
            perturbed = perturb_layout(
                layout=base_layout,
                strength=strength,
                rng=perturb_rng,
            )

            result = optimize_layout(
                layout=perturbed,
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
                    "Perturbed optimization "
                    "returned no score."
                )

            final_layout = (
                result.final_evaluation.layout
            )

            final_raw = raw_components(
                result.final_evaluation
            )

            signature = mapping_signature(
                final_layout
            )

            score_delta = (
                result.final_score
                - base_score
            )

            returned_to_base = (
                signature == base_signature
            )

            improves_weighted = (
                result.final_score
                < base_score
            )

            row: dict[str, object] = {
                "strength": strength,
                "trial": trial,
                "iterations": (
                    result.iteration_count
                ),
                "weighted_score": (
                    result.final_score
                ),
                "score_delta": score_delta,
                "transition": (
                    final_raw["transition"]
                ),
                "trigram": (
                    final_raw["trigram"]
                ),
                "finger": (
                    final_raw["finger"]
                ),
                "position": (
                    final_raw["position"]
                ),
                "signature": signature,
                "layout": final_layout,
                "returned_to_base": (
                    returned_to_base
                ),
                "improves_weighted": (
                    improves_weighted
                ),
            }

            rows.append(row)

            status = "BETTER" if improves_weighted else (
                "RETURN"
                if returned_to_base
                else "OTHER"
            )

            print(
                f"[{trial:02d}/"
                f"{TRIALS_PER_STRENGTH:02d}]"
                f" {status:6}"
                f" iter={result.iteration_count:3d}"
                f" total={result.final_score:9.4f}"
                f" delta={score_delta:+9.4f}"
                f" T={final_raw['transition']:8.4f}"
                f" Tri={final_raw['trigram']:8.4f}"
                f" F={final_raw['finger']:7.4f}"
                f" P={final_raw['position']:7.4f}"
            )

    print()
    print("=" * 110)
    print("PER-STRENGTH SUMMARY")
    print("=" * 110)

    for strength in PERTURBATION_STRENGTHS:
        strength_rows = [
            row
            for row in rows
            if row["strength"] == strength
        ]

        better = [
            row
            for row in strength_rows
            if row["improves_weighted"]
        ]

        returned = [
            row
            for row in strength_rows
            if row["returned_to_base"]
        ]

        signatures = {
            str(row["signature"])
            for row in strength_rows
        }

        best = min(
            strength_rows,
            key=lambda row: float(
                row["weighted_score"]
            ),
        )

        dominates_base_count = sum(
            dominates(
                row,
                {
                    "transition": (
                        base_raw["transition"]
                    ),
                    "trigram": (
                        base_raw["trigram"]
                    ),
                    "finger": (
                        base_raw["finger"]
                    ),
                    "position": (
                        base_raw["position"]
                    ),
                },
            )
            for row in strength_rows
        )

        print(
            f"strength={strength}"
            f" better={len(better):2d}/"
            f"{len(strength_rows)}"
            f" return={len(returned):2d}/"
            f"{len(strength_rows)}"
            f" unique={len(signatures):2d}"
            f" dominates_base="
            f"{dominates_base_count:2d}"
            f" best={float(best['weighted_score']):.6f}"
            f" improvement="
            f"{base_score - float(best['weighted_score']):.6f}"
        )

    endpoint_groups: dict[
        str,
        list[dict[str, object]],
    ] = defaultdict(list)

    for row in rows:
        endpoint_groups[
            str(row["signature"])
        ].append(row)

    unique_rows = [
        group[0]
        for group in endpoint_groups.values()
    ]

    base_row: dict[str, object] = {
        "strength": 0,
        "trial": 0,
        "weighted_score": base_score,
        "transition": base_raw["transition"],
        "trigram": base_raw["trigram"],
        "finger": base_raw["finger"],
        "position": base_raw["position"],
        "signature": base_signature,
        "layout": base_layout,
    }

    frontier = pareto_frontier(
        [base_row, *unique_rows]
    )

    best_overall = min(
        [base_row, *unique_rows],
        key=lambda row: float(
            row["weighted_score"]
        ),
    )

    print()
    print("=" * 110)
    print("GLOBAL SUMMARY")
    print("=" * 110)

    print(
        f"perturbation_runs     : "
        f"{len(rows)}"
    )
    print(
        f"unique endpoints      : "
        f"{len(unique_rows)}"
    )
    print(
        f"returned to base      : "
        f"{sum(bool(row['returned_to_base']) for row in rows)}"
    )
    print(
        f"weighted improvements : "
        f"{sum(bool(row['improves_weighted']) for row in rows)}"
    )
    print(
        f"Pareto solutions      : "
        f"{len(frontier)}"
        f" including base when applicable"
    )

    print()
    print("GLOBAL PARETO FRONTIER")
    print("-" * 110)

    frontier_sorted = sorted(
        frontier,
        key=lambda row: float(
            row["weighted_score"]
        ),
    )

    for index, row in enumerate(
        frontier_sorted,
        start=1,
    ):
        signature = str(
            row["signature"]
        )

        convergence_count = (
            1
            if row is base_row
            else len(
                endpoint_groups[
                    signature
                ]
            )
        )

        source = (
            "BASE"
            if row is base_row
            else (
                f"s{row['strength']}"
                f"/t{int(row['trial']):02d}"
            )
        )

        print(
            f"{index:2d}."
            f" count={convergence_count:2d}"
            f" total="
            f"{float(row['weighted_score']):9.4f}"
            f" T="
            f"{float(row['transition']):8.4f}"
            f" Tri="
            f"{float(row['trigram']):8.4f}"
            f" F="
            f"{float(row['finger']):7.4f}"
            f" P="
            f"{float(row['position']):7.4f}"
            f" source={source}"
        )

    print()
    print("=" * 110)
    print("BEST OVERALL")
    print("=" * 110)

    if best_overall is base_row:
        best_source = "BASE"
    else:
        best_source = (
            f"strength="
            f"{best_overall['strength']}"
            f" trial="
            f"{int(best_overall['trial']):02d}"
        )

    print(
        f"source={best_source}"
    )

    print(
        f"weighted_total="
        f"{float(best_overall['weighted_score']):.6f}"
    )

    print(
        f"improvement_over_base="
        f"{base_score - float(best_overall['weighted_score']):.6f}"
    )

    print(
        "raw="
        f"T={float(best_overall['transition']):.6f} "
        f"Tri={float(best_overall['trigram']):.6f} "
        f"F={float(best_overall['finger']):.6f} "
        f"P={float(best_overall['position']):.6f}"
    )

    print()
    print(
        mapping_signature(
            best_overall["layout"]
        )
    )


if __name__ == "__main__":
    main()
