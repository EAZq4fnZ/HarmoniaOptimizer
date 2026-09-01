from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from config.harmonia_position_costs import (
    make_harmonia_position_cost_profile,
)
from config_loader.constraint_config_loader import (
    ConstraintConfigLoader,
)
from config_loader.optimization_config_loader import (
    OptimizationConfigLoader,
)
from evaluator.candidate_evaluator import CandidateEvaluator
from evaluator.candidate_scorer import CandidateScorer
from evaluator.character_analyzer import CharacterAnalyzer
from evaluator.constraint_factory import ConstraintFactory
from evaluator.corpus_analyzer import CorpusAnalyzer
from evaluator.finger_load_pipeline import FingerLoadPipeline
from evaluator.key_position_evaluator import (
    KeyPositionEvaluator,
)
from evaluator.layout_evaluator import LayoutEvaluator
from evaluator.trigram_layout_evaluator import (
    TrigramLayoutEvaluator,
)
from models.candidate_score import CandidateScoreWeights
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry
from models.layout import Layout
from optimizer.local_search_optimizer import (
    LocalSearchOptimizer,
)

ROOT = Path(__file__).resolve().parents[1]

LAYOUTS = [
    "harmonia_v5_1b.json",
    "harmonia_v5_1b_vowels_balanced_seed.json",
    "harmonia_v5_1b_vowels_left_seed.json",
    "harmonia_v5_1b_vowels_split_seed.json",
]


@dataclass(frozen=True, slots=True)
class WeightProfile:
    name: str
    transition: float
    trigram: float
    finger: float
    position: float


PROFILES = (
    WeightProfile(
        name="baseline",
        transition=1.0,
        trigram=0.0,
        finger=1.0,
        position=0.0,
    ),
    WeightProfile(
        name="A",
        transition=1.0,
        trigram=1.0,
        finger=2.0,
        position=10.0,
    ),
    WeightProfile(
        name="B",
        transition=1.0,
        trigram=0.5,
        finger=2.0,
        position=10.0,
    ),
    WeightProfile(
        name="C",
        transition=1.0,
        trigram=1.0,
        finger=1.0,
        position=5.0,
    ),
    WeightProfile(
        name="D",
        transition=1.0,
        trigram=1.0,
        finger=2.0,
        position=5.0,
    ),
)


def load_text() -> str:
    corpus_path = ROOT / "corpus" / "sample.txt"

    if corpus_path.exists():
        return corpus_path.read_text(
            encoding="utf-8"
        )

    return (
        "konnichiwa watashi no namae wa harmonia desu "
        "this is a small temporary corpus for diagnostics "
        "typescript python rust javascript keyboard layout"
    )


def make_evaluator(
    profile: WeightProfile,
) -> CandidateEvaluator:
    config = OptimizationConfigLoader.load(
        ROOT / "config/optimization/default.json"
    )

    constraints = ConstraintConfigLoader.load(
        ROOT / "config/constraints/default.json"
    )

    weights = CandidateScoreWeights(
        transition_weight=profile.transition,
        trigram_weight=profile.trigram,
        finger_load_weight=profile.finger,
        position_weight=profile.position,
    )

    return CandidateEvaluator(
        constraint_set=ConstraintFactory.create(
            constraints
        ),
        layout_evaluator=LayoutEvaluator(
            config.transition_cost_weights
        ),
        finger_load_pipeline=FingerLoadPipeline(),
        candidate_scorer=CandidateScorer(weights),
        finger_load_budgets=config.finger_load_budgets,
        trigram_layout_evaluator=TrigramLayoutEvaluator(
            config.trigram_cost_weights
        ),
        key_position_evaluator=KeyPositionEvaluator(
            make_harmonia_position_cost_profile()
        ),
    )


def raw_components(
    evaluation,
) -> dict[str, float]:
    score = evaluation.candidate_score

    return {
        "transition": score.transition_score,
        "trigram": score.trigram_score,
        "finger": score.finger_load_score,
        "position": score.position_score,
    }


def mapping_signature(
    layout: Layout,
) -> str:
    return " ".join(
        f"{letter}={layout.mapping[letter]}"
        for letter in sorted(layout.mapping)
    )



RAW_SCORE_KEYS = (
    "transition",
    "trigram",
    "finger",
    "position",
)


def dominates(
    first: dict[str, object],
    second: dict[str, object],
) -> bool:
    first_scores = [
        float(first[key])
        for key in RAW_SCORE_KEYS
    ]
    second_scores = [
        float(second[key])
        for key in RAW_SCORE_KEYS
    ]

    no_worse = all(
        first_score <= second_score
        for first_score, second_score in zip(
            first_scores,
            second_scores,
            strict=True,
        )
    )

    strictly_better = any(
        first_score < second_score
        for first_score, second_score in zip(
            first_scores,
            second_scores,
            strict=True,
        )
    )

    return no_worse and strictly_better


def domination_statistics(
    rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []

    for row in rows:
        dominates_count = sum(
            dominates(row, other)
            for other in rows
            if other is not row
        )

        dominated_by_count = sum(
            dominates(other, row)
            for other in rows
            if other is not row
        )

        result.append(
            {
                "row": row,
                "dominates": dominates_count,
                "dominated_by": dominated_by_count,
                "pareto": dominated_by_count == 0,
            }
        )

    return result


def candidate_label(
    row: dict[str, object],
) -> str:
    return (
        f"{row['layout']} / "
        f"{row['profile']}"
    )


def main() -> None:
    corpus = Corpus(
        entries=(
            CorpusEntry(load_text()),
        )
    )

    analyzer = CorpusAnalyzer()

    transition_statistics = analyzer.analyze(
        corpus
    )
    trigram_statistics = analyzer.analyze_trigrams(
        corpus
    )
    character_statistics = (
        CharacterAnalyzer().analyze(corpus)
    )

    rows: list[dict[str, object]] = []

    for layout_name in LAYOUTS:
        initial_layout = Layout.load(
            ROOT / "config/layouts" / layout_name
        )

        print()
        print("=" * 100)
        print(layout_name.replace(".json", ""))
        print("=" * 100)

        for profile in PROFILES:
            evaluator = make_evaluator(profile)

            optimizer = LocalSearchOptimizer(
                candidate_evaluator=evaluator,
            )

            result = optimizer.optimize(
                layout=initial_layout,
                transition_statistics=transition_statistics,
                character_statistics=character_statistics,
                trigram_statistics=trigram_statistics,
            )

            initial_raw = raw_components(
                result.initial_evaluation
            )
            final_raw = raw_components(
                result.final_evaluation
            )

            row = {
                "layout": layout_name.replace(
                    ".json",
                    "",
                ),
                "profile": profile.name,
                "iterations": result.iteration_count,
                "weighted_initial": result.initial_score,
                "weighted_final": result.final_score,
                "transition": final_raw["transition"],
                "trigram": final_raw["trigram"],
                "finger": final_raw["finger"],
                "position": final_raw["position"],
                "d_transition": (
                    final_raw["transition"]
                    - initial_raw["transition"]
                ),
                "d_trigram": (
                    final_raw["trigram"]
                    - initial_raw["trigram"]
                ),
                "d_finger": (
                    final_raw["finger"]
                    - initial_raw["finger"]
                ),
                "d_position": (
                    final_raw["position"]
                    - initial_raw["position"]
                ),
                "final_layout": (
                    result.final_evaluation.layout
                ),
            }

            rows.append(row)

            print(
                f"{profile.name:9}"
                f" iter={result.iteration_count:3d}"
                f" trans={final_raw['transition']:8.4f}"
                f" tri={final_raw['trigram']:8.4f}"
                f" finger={final_raw['finger']:8.4f}"
                f" pos={final_raw['position']:8.4f}"
            )

            print(
                f"{'':9}"
                f" delta:"
                f" T={row['d_transition']:+8.4f}"
                f" Tri={row['d_trigram']:+8.4f}"
                f" F={row['d_finger']:+8.4f}"
                f" P={row['d_position']:+8.4f}"
            )

    print()
    print("=" * 100)
    print("RAW FINAL SCORE COMPARISON")
    print("=" * 100)

    print(
        f"{'start':34}"
        f"{'profile':>9}"
        f"{'iter':>6}"
        f"{'trans':>10}"
        f"{'tri':>10}"
        f"{'finger':>10}"
        f"{'pos':>10}"
    )

    print("-" * 89)

    for row in rows:
        print(
            f"{str(row['layout'])[:33]:34}"
            f"{row['profile']!s:>9}"
            f"{int(row['iterations']):6d}"
            f"{float(row['transition']):10.4f}"
            f"{float(row['trigram']):10.4f}"
            f"{float(row['finger']):10.4f}"
            f"{float(row['position']):10.4f}"
        )

    print()
    print("=" * 100)
    print("PARETO ANALYSIS")
    print("=" * 100)

    domination = domination_statistics(rows)

    print(
        f"{'candidate':49}"
        f"{'dominated by':>13}"
        f"{'dominates':>11}"
        f"{'pareto':>9}"
    )

    print("-" * 82)

    for item in sorted(
        domination,
        key=lambda value: (
            int(value["dominated_by"]),
            -int(value["dominates"]),
            candidate_label(value["row"]),
        ),
    ):
        row = item["row"]

        print(
            f"{candidate_label(row)[:48]:49}"
            f"{int(item['dominated_by']):13d}"
            f"{int(item['dominates']):11d}"
            f"{'YES' if item['pareto'] else '':>9}"
        )

    frontier = [
        item
        for item in domination
        if item["pareto"]
    ]

    print()
    print("Pareto frontier")
    print("-" * 100)

    for item in frontier:
        row = item["row"]

        print(
            f"{candidate_label(row)}"
            f"  T={float(row['transition']):.4f}"
            f" Tri={float(row['trigram']):.4f}"
            f" F={float(row['finger']):.4f}"
            f" P={float(row['position']):.4f}"
        )

    print()
    print("Profile summary")
    print("-" * 72)

    for profile in PROFILES:
        profile_items = [
            item
            for item in domination
            if item["row"]["profile"] == profile.name
        ]

        pareto_hits = sum(
            bool(item["pareto"])
            for item in profile_items
        )

        dominated_by_total = sum(
            int(item["dominated_by"])
            for item in profile_items
        )

        dominates_total = sum(
            int(item["dominates"])
            for item in profile_items
        )

        print(
            f"{profile.name:9}"
            f" pareto_hits={pareto_hits}/"
            f"{len(profile_items)}"
            f" dominated_by_total={dominated_by_total:3d}"
            f" dominates_total={dominates_total:3d}"
        )

    print()
    print("=" * 100)
    print("FINAL LAYOUTS")
    print("=" * 100)

    seen: dict[str, str] = {}

    for row in rows:
        final_layout = row["final_layout"]
        signature = mapping_signature(final_layout)

        key = (
            f"{row['layout']} / "
            f"{row['profile']}"
        )

        duplicate_of = seen.get(signature)

        print()
        print(key)

        if duplicate_of is not None:
            print(
                f"same final layout as: {duplicate_of}"
            )
        else:
            seen[signature] = key
            print(signature)


if __name__ == "__main__":
    main()
