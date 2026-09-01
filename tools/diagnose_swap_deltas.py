from __future__ import annotations

import math
from pathlib import Path
from statistics import mean, pstdev

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
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry
from models.layout import Layout
from optimizer.swap_candidate_generator import (
    SwapCandidateGenerator,
)

ROOT = Path(__file__).resolve().parents[1]

LAYOUTS = [
    "harmonia_v5_1b.json",
    "harmonia_v5_1b_vowels_balanced_seed.json",
    "harmonia_v5_1b_vowels_left_seed.json",
    "harmonia_v5_1b_vowels_split_seed.json",
]

COMPONENTS = (
    "transition",
    "trigram",
    "finger",
    "position",
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


def make_evaluator() -> CandidateEvaluator:
    config = OptimizationConfigLoader.load(
        ROOT / "config/optimization/default.json"
    )

    constraints = ConstraintConfigLoader.load(
        ROOT / "config/constraints/default.json"
    )

    return CandidateEvaluator(
        constraint_set=ConstraintFactory.create(
            constraints
        ),
        layout_evaluator=LayoutEvaluator(
            config.transition_cost_weights
        ),
        finger_load_pipeline=FingerLoadPipeline(),
        candidate_scorer=CandidateScorer(
            config.candidate_score_weights
        ),
        finger_load_budgets=config.finger_load_budgets,
        trigram_layout_evaluator=TrigramLayoutEvaluator(
            config.trigram_cost_weights
        ),
        key_position_evaluator=KeyPositionEvaluator(
            make_harmonia_position_cost_profile()
        ),
    )


def score_components(evaluation) -> dict[str, float]:
    score = evaluation.candidate_score

    return {
        "transition": score.transition_score,
        "trigram": score.trigram_score,
        "finger": score.finger_load_score,
        "position": score.position_score,
    }


def percentile(
    values: list[float],
    fraction: float,
) -> float:
    if not values:
        return 0.0

    ordered = sorted(values)

    if len(ordered) == 1:
        return ordered[0]

    index = fraction * (len(ordered) - 1)
    lower = math.floor(index)
    upper = math.ceil(index)

    if lower == upper:
        return ordered[lower]

    weight = index - lower

    return (
        ordered[lower] * (1.0 - weight)
        + ordered[upper] * weight
    )


def classify(
    values: list[float],
    epsilon: float = 1e-12,
) -> tuple[int, int, int]:
    improved = sum(
        value < -epsilon
        for value in values
    )
    unchanged = sum(
        abs(value) <= epsilon
        for value in values
    )
    worsened = sum(
        value > epsilon
        for value in values
    )

    return improved, unchanged, worsened



def pearson_correlation(
    xs: list[float],
    ys: list[float],
) -> float:
    if len(xs) != len(ys):
        raise ValueError(
            "Correlation inputs must have equal length."
        )

    if not xs:
        return 0.0

    mean_x = mean(xs)
    mean_y = mean(ys)

    centered_x = [
        value - mean_x
        for value in xs
    ]
    centered_y = [
        value - mean_y
        for value in ys
    ]

    numerator = sum(
        x * y
        for x, y in zip(
            centered_x,
            centered_y,
            strict=True,
        )
    )

    denominator_x = math.sqrt(
        sum(
            value * value
            for value in centered_x
        )
    )
    denominator_y = math.sqrt(
        sum(
            value * value
            for value in centered_y
        )
    )

    denominator = (
        denominator_x
        * denominator_y
    )

    if denominator == 0.0:
        return 0.0

    return numerator / denominator


def print_correlation_matrix(
    deltas: dict[str, list[float]],
) -> None:
    print("Correlation matrix")
    print("-" * 72)

    print(
        f"{'':12}"
        + "".join(
            f"{component[:10]:>12}"
            for component in COMPONENTS
        )
    )

    for row_component in COMPONENTS:
        print(
            f"{row_component:12}"
            + "".join(
                f"{pearson_correlation(
                    deltas[row_component],
                    deltas[column_component],
                ):12.3f}"
                for column_component in COMPONENTS
            )
        )


def direction(
    value: float,
    epsilon: float = 1e-12,
) -> int:
    if value < -epsilon:
        return -1

    if value > epsilon:
        return 1

    return 0


def print_tradeoff_statistics(
    deltas: dict[str, list[float]],
) -> None:
    print("Pairwise direction agreement")
    print("-" * 72)

    for index, first in enumerate(COMPONENTS):
        for second in COMPONENTS[index + 1:]:
            same_direction = 0
            tradeoff = 0
            neutral = 0

            first_improves_second_worsens = 0
            second_improves_first_worsens = 0
            both_improve = 0
            both_worsen = 0

            for first_delta, second_delta in zip(
                deltas[first],
                deltas[second],
                strict=True,
            ):
                first_direction = direction(
                    first_delta
                )
                second_direction = direction(
                    second_delta
                )

                if (
                    first_direction == 0
                    or second_direction == 0
                ):
                    neutral += 1
                    continue

                if (
                    first_direction
                    == second_direction
                ):
                    same_direction += 1

                    if first_direction < 0:
                        both_improve += 1
                    else:
                        both_worsen += 1
                else:
                    tradeoff += 1

                    if (
                        first_direction < 0
                        and second_direction > 0
                    ):
                        first_improves_second_worsens += 1
                    else:
                        second_improves_first_worsens += 1

            comparable = (
                same_direction
                + tradeoff
            )

            if comparable:
                agreement_rate = (
                    same_direction
                    / comparable
                )
                tradeoff_rate = (
                    tradeoff
                    / comparable
                )
            else:
                agreement_rate = 0.0
                tradeoff_rate = 0.0

            print(
                f"{first:10} <-> {second:10}"
                f" corr={pearson_correlation(
                    deltas[first],
                    deltas[second],
                ):7.3f}"
                f" agree={agreement_rate:6.1%}"
                f" tradeoff={tradeoff_rate:6.1%}"
                f" neutral={neutral:3d}"
            )

            print(
                f"{'':25}"
                f"both_better={both_improve:3d}"
                f" both_worse={both_worsen:3d}"
                f" {first[:5]}+/{second[:5]}-="
                f"{first_improves_second_worsens:3d}"
                f" {second[:5]}+/{first[:5]}-="
                f"{second_improves_first_worsens:3d}"
            )


def print_component_statistics(
    component: str,
    values: list[float],
) -> None:
    absolute = [
        abs(value)
        for value in values
    ]

    improved, unchanged, worsened = classify(values)

    print(
        f"{component:11}"
        f" min={min(values):9.5f}"
        f" mean={mean(values):9.5f}"
        f" max={max(values):9.5f}"
        f" std={pstdev(values):9.5f}"
    )

    print(
        f"{'|delta|':11}"
        f" p50={percentile(absolute, 0.50):9.5f}"
        f" p75={percentile(absolute, 0.75):9.5f}"
        f" p90={percentile(absolute, 0.90):9.5f}"
        f" p95={percentile(absolute, 0.95):9.5f}"
        f" max={max(absolute):9.5f}"
    )

    print(
        f"{'direction':11}"
        f" better={improved:3d}"
        f" same={unchanged:3d}"
        f" worse={worsened:3d}"
    )


def diagnose_layout(
    layout_name: str,
    evaluator: CandidateEvaluator,
    generator: SwapCandidateGenerator,
    transition_statistics,
    character_statistics,
    trigram_statistics,
) -> None:
    layout = Layout.load(
        ROOT / "config/layouts" / layout_name
    )

    base_evaluation = evaluator.evaluate(
        layout=layout,
        transition_statistics=transition_statistics,
        character_statistics=character_statistics,
        trigram_statistics=trigram_statistics,
    )

    base = score_components(base_evaluation)

    deltas = {
        component: []
        for component in COMPONENTS
    }

    candidates = generator.generate_candidates(
        layout
    )

    for candidate in candidates:
        evaluation = evaluator.evaluate(
            layout=candidate.layout,
            transition_statistics=transition_statistics,
            character_statistics=character_statistics,
            trigram_statistics=trigram_statistics,
        )

        scores = score_components(evaluation)

        for component in COMPONENTS:
            deltas[component].append(
                scores[component]
                - base[component]
            )

    print()
    print("=" * 92)
    print(layout_name.replace(".json", ""))
    print("=" * 92)

    print(
        "base:"
        f" transition={base['transition']:.6f}"
        f" trigram={base['trigram']:.6f}"
        f" finger={base['finger']:.6f}"
        f" position={base['position']:.6f}"
    )

    print(
        f"one-swap candidates: {len(candidates)}"
    )

    print()

    for component in COMPONENTS:
        print_component_statistics(
            component,
            deltas[component],
        )
        print()

    print_correlation_matrix(deltas)
    print()

    print_tradeoff_statistics(deltas)
    print()


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

    evaluator = make_evaluator()
    generator = SwapCandidateGenerator()

    for layout_name in LAYOUTS:
        diagnose_layout(
            layout_name=layout_name,
            evaluator=evaluator,
            generator=generator,
            transition_statistics=transition_statistics,
            character_statistics=character_statistics,
            trigram_statistics=trigram_statistics,
        )


if __name__ == "__main__":
    main()
