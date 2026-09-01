from __future__ import annotations

import math
from random import Random
from statistics import mean, pstdev

from evaluator.character_analyzer import CharacterAnalyzer
from evaluator.corpus_analyzer import CorpusAnalyzer
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry
from models.layout import Layout
from optimizer.local_search_optimizer import LocalSearchOptimizer
from optimizer.swap_candidate_generator import SwapCandidateGenerator
from tools.diagnose_multistart import (
    PROFILE,
    RANDOM_SEED,
    make_random_layout,
)
from tools.diagnose_weight_sweep import (
    ROOT,
    load_text,
    make_evaluator,
    raw_components,
)

SCORE_EPSILON = 1e-12

PERCENTILES = (
    0.25,
    0.50,
    0.75,
    0.90,
    0.95,
)

INITIAL_ACCEPTANCE_TARGETS = (
    0.50,
    0.80,
    0.90,
)

FINAL_ACCEPTANCE_TARGETS = (
    0.01,
    0.05,
    0.10,
)


def percentile(
    values: list[float],
    probability: float,
) -> float:
    if not values:
        raise ValueError(
            "Cannot calculate percentile "
            "of an empty sequence."
        )

    if not 0.0 <= probability <= 1.0:
        raise ValueError(
            "probability must be between 0 and 1"
        )

    ordered = sorted(values)

    if len(ordered) == 1:
        return ordered[0]

    position = probability * (
        len(ordered) - 1
    )

    lower_index = math.floor(position)
    upper_index = math.ceil(position)

    lower = ordered[lower_index]
    upper = ordered[upper_index]

    if lower_index == upper_index:
        return lower

    fraction = position - lower_index

    return lower + (
        upper - lower
    ) * fraction


def temperature_for_acceptance(
    delta: float,
    probability: float,
) -> float:
    if delta <= 0.0:
        raise ValueError(
            "delta must be positive"
        )

    if not 0.0 < probability < 1.0:
        raise ValueError(
            "probability must be between 0 and 1"
        )

    return -delta / math.log(probability)


def acceptance_probability(
    delta: float,
    temperature: float,
) -> float:
    if delta <= 0.0:
        return 1.0

    if temperature <= 0.0:
        return 0.0

    return math.exp(
        -delta / temperature
    )


def main() -> None:
    print(
        "Annealing temperature diagnostic"
        f"  profile={PROFILE.name}"
        f"  weights="
        f"{PROFILE.transition:g}/"
        f"{PROFILE.trigram:g}/"
        f"{PROFILE.finger:g}/"
        f"{PROFILE.position:g}"
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

    base_evaluator = make_evaluator(PROFILE)

    optimizer = LocalSearchOptimizer(
        candidate_evaluator=base_evaluator,
    )

    base_result = optimizer.optimize(
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

    base_score = base_result.final_score

    base_raw = raw_components(
        base_result.final_evaluation
    )

    print()
    print("=" * 100)
    print("BASE LOCAL OPTIMUM")
    print("=" * 100)

    print(
        f"iterations={base_result.iteration_count}"
        f" total={base_score:.9f}"
        f" T={base_raw['transition']:.6f}"
        f" Tri={base_raw['trigram']:.6f}"
        f" F={base_raw['finger']:.6f}"
        f" P={base_raw['position']:.6f}"
    )

    evaluator = make_evaluator(PROFILE)

    generator = SwapCandidateGenerator()

    candidates = generator.generate_candidates(
        base_layout
    )

    deltas: list[float] = []
    improving: list[float] = []
    neutral: list[float] = []
    worsening: list[float] = []

    for candidate in candidates:
        evaluation = evaluator.evaluate(
            layout=candidate.layout,
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
            continue

        delta = (
            evaluation.score
            - base_score
        )

        deltas.append(delta)

        if delta < -SCORE_EPSILON:
            improving.append(delta)
        elif delta > SCORE_EPSILON:
            worsening.append(delta)
        else:
            neutral.append(delta)

    print()
    print("=" * 100)
    print("ONE-SWAP DISTRIBUTION")
    print("=" * 100)

    print(
        f"generated candidates : "
        f"{len(candidates)}"
    )
    print(
        f"evaluated candidates : "
        f"{len(deltas)}"
    )
    print(
        f"improving            : "
        f"{len(improving)}"
    )
    print(
        f"neutral              : "
        f"{len(neutral)}"
    )
    print(
        f"worsening            : "
        f"{len(worsening)}"
    )

    if deltas:
        print()
        print(
            f"all delta:"
            f" min={min(deltas):.9f}"
            f" mean={mean(deltas):.9f}"
            f" max={max(deltas):.9f}"
            f" std={pstdev(deltas):.9f}"
        )

    if not worsening:
        print()
        print(
            "No worsening swaps were found; "
            "temperature estimation is unavailable."
        )
        return

    print()
    print("=" * 100)
    print("WORSENING DELTA PERCENTILES")
    print("=" * 100)

    percentile_values: dict[
        float,
        float,
    ] = {}

    for probability in PERCENTILES:
        value = percentile(
            worsening,
            probability,
        )

        percentile_values[
            probability
        ] = value

        print(
            f"p{int(probability * 100):02d}"
            f" = {value:.9f}"
        )

    median_delta = percentile_values[0.50]

    print()
    print("=" * 100)
    print(
        "TEMPERATURES BASED ON "
        "MEDIAN WORSENING DELTA"
    )
    print("=" * 100)

    print(
        f"median worsening delta = "
        f"{median_delta:.9f}"
    )

    print()
    print("Initial-temperature candidates")
    print("-" * 60)

    initial_temperatures: dict[
        float,
        float,
    ] = {}

    for probability in (
        INITIAL_ACCEPTANCE_TARGETS
    ):
        temperature = (
            temperature_for_acceptance(
                delta=median_delta,
                probability=probability,
            )
        )

        initial_temperatures[
            probability
        ] = temperature

        print(
            f"accept median worsening move "
            f"{probability * 100:5.1f}%"
            f" -> T={temperature:.9f}"
        )

    print()
    print("Final-temperature candidates")
    print("-" * 60)

    final_temperatures: dict[
        float,
        float,
    ] = {}

    for probability in (
        FINAL_ACCEPTANCE_TARGETS
    ):
        temperature = (
            temperature_for_acceptance(
                delta=median_delta,
                probability=probability,
            )
        )

        final_temperatures[
            probability
        ] = temperature

        print(
            f"accept median worsening move "
            f"{probability * 100:5.1f}%"
            f" -> T={temperature:.9f}"
        )

    recommended_initial = (
        initial_temperatures[0.80]
    )

    recommended_final = (
        final_temperatures[0.01]
    )

    print()
    print("=" * 100)
    print("RECOMMENDED DIAGNOSTIC RANGE")
    print("=" * 100)

    print(
        f"T_initial={recommended_initial:.9f}"
    )
    print(
        f"T_final  ={recommended_final:.9f}"
    )

    print()
    print(
        "Acceptance probabilities at "
        "recommended initial temperature"
    )
    print("-" * 70)

    for probability in PERCENTILES:
        delta = percentile_values[
            probability
        ]

        acceptance = (
            acceptance_probability(
                delta=delta,
                temperature=(
                    recommended_initial
                ),
            )
        )

        print(
            f"p{int(probability * 100):02d}"
            f" delta={delta:.9f}"
            f" acceptance="
            f"{acceptance * 100:6.2f}%"
        )

    print()
    print(
        "Acceptance probabilities at "
        "recommended final temperature"
    )
    print("-" * 70)

    for probability in PERCENTILES:
        delta = percentile_values[
            probability
        ]

        acceptance = (
            acceptance_probability(
                delta=delta,
                temperature=(
                    recommended_final
                ),
            )
        )

        print(
            f"p{int(probability * 100):02d}"
            f" delta={delta:.9f}"
            f" acceptance="
            f"{acceptance * 100:6.2f}%"
        )

    print()
    print("=" * 100)
    print("GEOMETRIC COOLING REFERENCE")
    print("=" * 100)

    for steps in (
        1_000,
        5_000,
        10_000,
        25_000,
    ):
        cooling_rate = (
            recommended_final
            / recommended_initial
        ) ** (
            1.0 / steps
        )

        print(
            f"steps={steps:6d}"
            f" alpha={cooling_rate:.9f}"
        )


if __name__ == "__main__":
    main()
