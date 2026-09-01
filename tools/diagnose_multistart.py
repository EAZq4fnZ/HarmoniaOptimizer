from __future__ import annotations

from collections import defaultdict
from random import Random

from evaluator.character_analyzer import CharacterAnalyzer
from evaluator.corpus_analyzer import CorpusAnalyzer
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry
from models.layout import Layout
from optimizer.local_search_optimizer import LocalSearchOptimizer
from tools.diagnose_weight_sweep import (
    ROOT,
    WeightProfile,
    dominates,
    load_text,
    make_evaluator,
    mapping_signature,
    raw_components,
)

PROFILE = WeightProfile(
    name="C",
    transition=1.0,
    trigram=1.0,
    finger=1.0,
    position=5.0,
)

RANDOM_SEED = 20260901
RANDOM_START_COUNT = 20

EXISTING_LAYOUTS = (
    "harmonia_v5_1b.json",
    "harmonia_v5_1b_vowels_balanced_seed.json",
    "harmonia_v5_1b_vowels_left_seed.json",
    "harmonia_v5_1b_vowels_split_seed.json",
)

RAW_SCORE_KEYS = (
    "transition",
    "trigram",
    "finger",
    "position",
)


def make_random_layout(
    base: Layout,
    rng: Random,
    index: int,
) -> Layout:
    letters = sorted(base.mapping)
    positions = [
        base.mapping[letter]
        for letter in letters
    ]

    rng.shuffle(positions)

    mapping = dict(
        zip(
            letters,
            positions,
            strict=True,
        )
    )

    return Layout(
        name=f"random_start_{index:02d}",
        version=base.version,
        layer=base.layer,
        description=(
            "Deterministic random start for "
            "multi-start diagnostics."
        ),
        mapping=mapping,
    )


def make_starts() -> list[tuple[str, Layout]]:
    starts: list[tuple[str, Layout]] = []

    for filename in EXISTING_LAYOUTS:
        layout = Layout.load(
            ROOT / "config/layouts" / filename
        )

        starts.append(
            (
                filename.replace(".json", ""),
                layout,
            )
        )

    base = Layout.load(
        ROOT
        / "config/layouts"
        / "harmonia_v5_1b.json"
    )

    rng = Random(RANDOM_SEED)

    existing_signatures = {
        mapping_signature(layout)
        for _, layout in starts
    }

    random_index = 1

    while (
        random_index
        <= RANDOM_START_COUNT
    ):
        candidate = make_random_layout(
            base=base,
            rng=rng,
            index=random_index,
        )

        signature = mapping_signature(candidate)

        if signature in existing_signatures:
            continue

        existing_signatures.add(signature)

        starts.append(
            (
                f"random_{random_index:02d}",
                candidate,
            )
        )

        random_index += 1

    return starts


def pareto_frontier(
    rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    return [
        row
        for row in rows
        if not any(
            dominates(other, row)
            for other in rows
            if other is not row
        )
    ]


def main() -> None:
    print(
        "Multi-start diagnostic"
        f"  profile={PROFILE.name}"
        f"  weights="
        f"{PROFILE.transition:g}/"
        f"{PROFILE.trigram:g}/"
        f"{PROFILE.finger:g}/"
        f"{PROFILE.position:g}"
    )

    print(
        f"random_seed={RANDOM_SEED}"
        f" random_starts={RANDOM_START_COUNT}"
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

    starts = make_starts()

    print(
        f"total_starts={len(starts)}"
    )
    print()

    rows: list[dict[str, object]] = []

    for index, (
        start_name,
        start_layout,
    ) in enumerate(
        starts,
        start=1,
    ):
        evaluator = make_evaluator(PROFILE)

        optimizer = LocalSearchOptimizer(
            candidate_evaluator=evaluator,
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

        final_raw = raw_components(
            result.final_evaluation
        )

        final_layout = (
            result.final_evaluation.layout
        )

        signature = mapping_signature(
            final_layout
        )

        if result.final_score is None:
            raise RuntimeError(
                f"{start_name}: final score is None"
            )

        row: dict[str, object] = {
            "start": start_name,
            "iterations": (
                result.iteration_count
            ),
            "weighted_score": (
                result.final_score
            ),
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
        }

        rows.append(row)

        print(
            f"[{index:02d}/{len(starts):02d}] "
            f"{start_name:38}"
            f" iter={result.iteration_count:3d}"
            f" total={result.final_score:9.4f}"
            f" T={final_raw['transition']:8.4f}"
            f" Tri={final_raw['trigram']:8.4f}"
            f" F={final_raw['finger']:7.4f}"
            f" P={final_raw['position']:7.4f}"
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

    frontier = pareto_frontier(
        unique_rows
    )

    best_weighted = min(
        unique_rows,
        key=lambda row: float(
            row["weighted_score"]
        ),
    )

    print()
    print("=" * 110)
    print("SUMMARY")
    print("=" * 110)

    print(
        f"starts                : "
        f"{len(rows)}"
    )
    print(
        f"unique final layouts  : "
        f"{len(unique_rows)}"
    )
    print(
        f"duplicate convergences: "
        f"{len(rows) - len(unique_rows)}"
    )
    print(
        f"Pareto final layouts  : "
        f"{len(frontier)}"
    )

    print()
    print("CONVERGENCE COUNTS")
    print("-" * 110)

    ordered_groups = sorted(
        endpoint_groups.values(),
        key=lambda group: (
            -len(group),
            float(
                group[0]["weighted_score"]
            ),
        ),
    )

    for endpoint_index, group in enumerate(
        ordered_groups,
        start=1,
    ):
        representative = group[0]

        starts_text = ", ".join(
            str(row["start"])
            for row in group
        )

        print(
            f"endpoint_{endpoint_index:02d}"
            f" count={len(group):2d}"
            f" total="
            f"{float(representative['weighted_score']):9.4f}"
            f" T="
            f"{float(representative['transition']):8.4f}"
            f" Tri="
            f"{float(representative['trigram']):8.4f}"
            f" F="
            f"{float(representative['finger']):7.4f}"
            f" P="
            f"{float(representative['position']):7.4f}"
        )

        print(
            f"    starts: {starts_text}"
        )

    print()
    print("PARETO FRONTIER")
    print("-" * 110)

    frontier_sorted = sorted(
        frontier,
        key=lambda row: float(
            row["weighted_score"]
        ),
    )

    for rank, row in enumerate(
        frontier_sorted,
        start=1,
    ):
        convergence_count = len(
            endpoint_groups[
                str(row["signature"])
            ]
        )

        print(
            f"{rank:2d}."
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
            f" from={row['start']}"
        )

    print()
    print("BEST WEIGHTED FINAL LAYOUT")
    print("-" * 110)

    print(
        f"start={best_weighted['start']}"
    )
    print(
        f"weighted_total="
        f"{float(best_weighted['weighted_score']):.6f}"
    )
    print(
        "raw="
        f"T={float(best_weighted['transition']):.6f} "
        f"Tri={float(best_weighted['trigram']):.6f} "
        f"F={float(best_weighted['finger']):.6f} "
        f"P={float(best_weighted['position']):.6f}"
    )

    print()
    print(
        mapping_signature(
            best_weighted["layout"]
        )
    )


if __name__ == "__main__":
    main()
