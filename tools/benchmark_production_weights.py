from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from evaluator.character_analyzer import CharacterAnalyzer
from evaluator.corpus_analyzer import CorpusAnalyzer
from models.candidate_score import CandidateScoreWeights
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry
from models.layout import Layout
from optimizer.local_search_optimizer import LocalSearchOptimizer
from optimizer.random_start_layout_factory import (
    RandomStartLayoutFactory,
)
from tools.diagnose_weight_sweep import (
    ROOT,
    load_text,
    make_evaluator,
    mapping_signature,
    raw_components,
)

RUNS = 16
MAX_ITERATIONS = 30
SEED = 20260908


@dataclass(frozen=True)
class Profile:
    name: str
    transition: float
    trigram: float
    finger: float
    position: float

    @property
    def weights(self) -> CandidateScoreWeights:
        return CandidateScoreWeights(
            transition_weight=self.transition,
            trigram_weight=self.trigram,
            finger_load_weight=self.finger,
            position_weight=self.position,
        )


PROFILES = (
    Profile(
        name="baseline",
        transition=1.0,
        trigram=0.0,
        finger=1.0,
        position=0.0,
    ),
    Profile(
        name="C",
        transition=1.0,
        trigram=1.0,
        finger=1.0,
        position=5.0,
    ),
    Profile(
        name="D",
        transition=1.0,
        trigram=1.0,
        finger=2.0,
        position=5.0,
    ),
)


def dominates(
    a: dict[str, float],
    b: dict[str, float],
) -> bool:
    keys = (
        "transition",
        "trigram",
        "finger",
        "position",
    )

    no_worse = all(
        a[key] <= b[key]
        for key in keys
    )

    strictly_better = any(
        a[key] < b[key]
        for key in keys
    )

    return no_worse and strictly_better


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

    factory = RandomStartLayoutFactory(
        seed=SEED
    )

    rows: list[dict[str, object]] = []

    for profile in PROFILES:
        for run_index in range(RUNS):
            start_layout = factory.create(
                base_layout=base_layout,
                run_index=run_index,
            )

            optimizer = LocalSearchOptimizer(
                candidate_evaluator=(
                    make_evaluator(
                        profile
                    )
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

            components = raw_components(
                result.final_evaluation
            )

            rows.append(
                {
                    "profile": profile.name,
                    "run": run_index,
                    "score": result.final_score,
                    "layout": (
                        result.final_evaluation.layout
                    ),
                    **components,
                }
            )

    print(
        "profile      mean_total   best_total"
        "      T_best    Tri_best"
        "      F_best      P_best"
    )
    print("-" * 92)

    profile_best_rows = []

    for profile in PROFILES:
        selected = [
            row
            for row in rows
            if row["profile"] == profile.name
        ]

        best = min(
            selected,
            key=lambda row: float(
                row["score"]
            ),
        )

        profile_best_rows.append(best)

        mean_total = mean(
            float(row["score"])
            for row in selected
        )

        print(
            f"{profile.name:10}"
            f"  {mean_total:11.6f}"
            f"  {float(best['score']):11.6f}"
            f"  {float(best['transition']):10.6f}"
            f"  {float(best['trigram']):10.6f}"
            f"  {float(best['finger']):10.6f}"
            f"  {float(best['position']):10.6f}"
        )

    print()
    print("Pareto relations between profile-best layouts")
    print("-" * 52)

    for a in profile_best_rows:
        for b in profile_best_rows:
            if a is b:
                continue

            a_components = {
                key: float(a[key])
                for key in (
                    "transition",
                    "trigram",
                    "finger",
                    "position",
                )
            }

            b_components = {
                key: float(b[key])
                for key in (
                    "transition",
                    "trigram",
                    "finger",
                    "position",
                )
            }

            if dominates(
                a_components,
                b_components,
            ):
                print(
                    f"{a['profile']} dominates "
                    f"{b['profile']}"
                )

    print()
    print("Best mappings")
    print("-" * 52)

    for row in profile_best_rows:
        print()
        print(
            f"[{row['profile']}]"
            f" score={float(row['score']):.9f}"
        )
        print(
            mapping_signature(
                row["layout"]
            )
        )


if __name__ == "__main__":
    main()
