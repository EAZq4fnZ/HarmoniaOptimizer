# tools/benchmark_prepared_transitions.py

from __future__ import annotations

import argparse
import time
from collections.abc import Callable

from evaluator.fast_layout_score_evaluator import (
    FastLayoutScoreEvaluator,
)
from evaluator.transition_statistics import (
    TransitionStatistics,
)
from models.layout import Layout
from models.transition_cost import (
    TransitionCostWeights,
)


def make_layout() -> Layout:
    return Layout(
        name="benchmark",
        description="Prepared transition benchmark",
        version="1.0",
        layer="L0",
        mapping={
            "A": "L-I-H-3",
            "B": "L-M-H-2",
            "C": "L-R-H-1",
            "D": "L-P-H-1",
            "E": "R-I-H-3",
            "F": "R-M-H-2",
            "G": "R-R-H-1",
            "H": "R-P-H-1",
            "I": "L-I-T-3",
            "J": "L-M-T-2",
            "K": "L-R-T-1",
            "L": "L-P-T-1",
            "M": "R-I-T-3",
            "N": "R-M-T-2",
            "O": "R-R-T-1",
            "P": "R-P-T-1",
            "Q": "L-I-B-3",
            "R": "L-M-B-2",
            "S": "L-R-B-1",
            "T": "L-P-B-1",
            "U": "R-I-B-3",
            "V": "R-M-B-2",
            "W": "R-R-B-1",
            "X": "R-P-B-1",
            "Y": "L-I-H-4",
            "Z": "R-I-H-4",
        },
    )


def make_weights() -> TransitionCostWeights:
    return TransitionCostWeights(
        same_finger_penalty=2.0,
        same_hand_penalty=1.0,
        row_change_penalty=0.5,
        alternation_reward=0.25,
        inward_roll_reward=0.4,
        outward_roll_reward=0.2,
    )


def make_statistics() -> TransitionStatistics:
    """
    Create a dense A-Z transition table.

    All 26 x 26 transitions are present so the benchmark exercises
    the expensive exhaustive-search case.
    """

    statistics = TransitionStatistics()

    counts: dict[
        tuple[str, str],
        int,
    ] = {}

    for source_index in range(26):
        source = chr(
            ord("A") + source_index
        )

        for target_index in range(26):
            target = chr(
                ord("A") + target_index
            )

            counts[
                (
                    source,
                    target,
                )
            ] = (
                (
                    source_index * 7
                    + target_index * 11
                )
                % 17
            ) + 1

    statistics.add(
        counts
    )

    return statistics


def build_integer_positions(
    evaluator: FastLayoutScoreEvaluator,
    layout: Layout,
) -> tuple[
    list[int],
    tuple[
        tuple[float, ...],
        ...,
    ],
]:
    string_positions: list[
        str | None
    ] = [
        None
    ] * 26

    for (
        letter,
        position,
    ) in layout.mapping.items():
        letter_index = (
            ord(letter.upper())
            - ord("A")
        )

        if 0 <= letter_index < 26:
            string_positions[
                letter_index
            ] = position

    logical_positions = tuple(
        position
        for position in string_positions
        if position is not None
    )

    (
        position_indexes,
        cost_matrix,
    ) = evaluator.build_position_index(
        logical_positions
    )

    integer_positions = list(
        evaluator.convert_to_position_indexes(
            string_positions,
            position_indexes,
        )
    )

    return (
        integer_positions,
        cost_matrix,
    )


def letter_index(
    letter: str,
) -> int:
    return (
        ord(letter)
        - ord("A")
    )


def make_five_letter_candidate(
    base_positions: list[int],
) -> tuple[
    list[int],
    tuple[int, ...],
]:
    """
    Rotate the five vowel positions.

    This changes exactly A/E/I/O/U.
    """

    candidate = list(
        base_positions
    )

    changed = tuple(
        letter_index(letter)
        for letter in (
            "A",
            "E",
            "I",
            "O",
            "U",
        )
    )

    (
        a_index,
        e_index,
        i_index,
        o_index,
        u_index,
    ) = changed

    (
        candidate[a_index],
        candidate[e_index],
        candidate[i_index],
        candidate[o_index],
        candidate[u_index],
    ) = (
        base_positions[e_index],
        base_positions[i_index],
        base_positions[o_index],
        base_positions[u_index],
        base_positions[a_index],
    )

    return (
        candidate,
        changed,
    )


def make_ten_letter_candidate(
    base_positions: list[int],
) -> tuple[
    list[int],
    tuple[int, ...],
]:
    """
    Change five vowels plus five consonants.

    This approximates a vowel-seed candidate where consonants are
    displaced from the selected vowel positions.
    """

    candidate = list(
        base_positions
    )

    letters = (
        "A",
        "E",
        "I",
        "O",
        "U",
        "B",
        "F",
        "J",
        "N",
        "V",
    )

    changed = tuple(
        letter_index(letter)
        for letter in letters
    )

    original_values = tuple(
        base_positions[index]
        for index in changed
    )

    rotated_values = (
        original_values[1:]
        + original_values[:1]
    )

    for (
        index,
        position,
    ) in zip(
        changed,
        rotated_values,
        strict=True,
    ):
        candidate[
            index
        ] = position

    return (
        candidate,
        changed,
    )


def benchmark(
    function: Callable[[], object],
    iterations: int,
    repeats: int,
) -> tuple[
    float,
    object,
]:
    best_elapsed = float(
        "inf"
    )

    best_result: (
        object | None
    ) = None

    for _ in range(
        repeats
    ):
        start = (
            time.perf_counter()
        )

        current_result: (
            object | None
        ) = None

        for _ in range(
            iterations
        ):
            current_result = (
                function()
            )

        elapsed = (
            time.perf_counter()
            - start
        )

        if elapsed < best_elapsed:
            best_elapsed = elapsed
            best_result = (
                current_result
            )

    assert (
        best_result is not None
    )

    return (
        best_elapsed,
        best_result,
    )


def assert_same_score(
    first: object,
    second: object,
) -> None:
    first_total = first.total_cost
    second_total = second.total_cost

    first_evaluated = first.evaluated_weight
    second_evaluated = second.evaluated_weight

    first_skipped = first.skipped_weight
    second_skipped = second.skipped_weight

    total_difference = abs(
        first_total
        - second_total
    )

    evaluated_difference = abs(
        first_evaluated
        - second_evaluated
    )

    skipped_difference = abs(
        first_skipped
        - second_skipped
    )

    tolerance = 1e-9

    if (
        total_difference > tolerance
        or evaluated_difference > tolerance
        or skipped_difference > tolerance
    ):
        raise RuntimeError(
            "\n"
            "Benchmark evaluation paths returned "
            "different results.\n"
            "\n"
            f"first.total_cost:       "
            f"{first_total!r}\n"
            f"second.total_cost:      "
            f"{second_total!r}\n"
            f"total difference:       "
            f"{total_difference:.16g}\n"
            "\n"
            f"first.evaluated_weight: "
            f"{first_evaluated!r}\n"
            f"second.evaluated_weight:"
            f" {second_evaluated!r}\n"
            f"evaluated difference:   "
            f"{evaluated_difference:.16g}\n"
            "\n"
            f"first.skipped_weight:   "
            f"{first_skipped!r}\n"
            f"second.skipped_weight:  "
            f"{second_skipped!r}\n"
            f"skipped difference:     "
            f"{skipped_difference:.16g}"
        )


def run_case(
    *,
    title: str,
    evaluator: FastLayoutScoreEvaluator,
    candidate_positions: list[int],
    changed_indexes: tuple[int, ...],
    cost_matrix: tuple[
        tuple[float, ...],
        ...,
    ],
    statistics: TransitionStatistics,
    prepared,
    prepared_delta_baseline,
    iterations: int,
    repeats: int,
) -> None:
    position_result = (
        evaluator
        .evaluate_position_indexed(
            candidate_positions,
            cost_matrix,
            statistics,
        )
    )

    prepared_result = (
        evaluator
        .evaluate_prepared_position_indexed(
            candidate_positions,
            cost_matrix,
            prepared,
        )
    )

    delta_result = (
        evaluator
        .evaluate_prepared_position_indexed_delta(
            candidate_positions,
            cost_matrix,
            prepared_delta_baseline,
            changed_indexes,
        )
    )

    assert_same_score(
        position_result,
        prepared_result,
    )

    assert_same_score(
        prepared_result,
        delta_result,
    )

    # Warm up all paths.
    for _ in range(
        10_000
    ):
        evaluator.evaluate_position_indexed(
            candidate_positions,
            cost_matrix,
            statistics,
        )

        evaluator.evaluate_prepared_position_indexed(
            candidate_positions,
            cost_matrix,
            prepared,
        )

        evaluator.evaluate_prepared_position_indexed_delta(
            candidate_positions,
            cost_matrix,
            prepared_delta_baseline,
            changed_indexes,
        )

    position_elapsed, _ = benchmark(
        lambda: (
            evaluator
            .evaluate_position_indexed(
                candidate_positions,
                cost_matrix,
                statistics,
            )
        ),
        iterations,
        repeats,
    )

    prepared_elapsed, _ = benchmark(
        lambda: (
            evaluator
            .evaluate_prepared_position_indexed(
                candidate_positions,
                cost_matrix,
                prepared,
            )
        ),
        iterations,
        repeats,
    )

    delta_elapsed, _ = benchmark(
        lambda: (
            evaluator
            .evaluate_prepared_position_indexed_delta(
                candidate_positions,
                cost_matrix,
                prepared_delta_baseline,
                changed_indexes,
            )
        ),
        iterations,
        repeats,
    )

    position_rate = (
        iterations
        / position_elapsed
    )

    prepared_rate = (
        iterations
        / prepared_elapsed
    )

    delta_rate = (
        iterations
        / delta_elapsed
    )

    prepared_speedup = (
        position_elapsed
        / prepared_elapsed
    )

    delta_vs_position = (
        position_elapsed
        / delta_elapsed
    )

    delta_vs_prepared = (
        prepared_elapsed
        / delta_elapsed
    )

    print()
    print(title)
    print("=" * len(title))
    print()

    print(
        f"Changed letters:   "
        f"{len(changed_indexes):,}"
    )

    print(
        f"Iterations:        "
        f"{iterations:,}"
    )

    print(
        f"Repeats:           "
        f"{repeats:,}"
    )

    print()

    print(
        f"Position indexed:  "
        f"{position_elapsed:.6f} s"
    )

    print(
        f"Prepared full:     "
        f"{prepared_elapsed:.6f} s"
    )

    print(
        f"Prepared delta:    "
        f"{delta_elapsed:.6f} s"
    )

    print()

    print(
        f"Position rate:     "
        f"{position_rate:,.0f} eval/s"
    )

    print(
        f"Prepared rate:     "
        f"{prepared_rate:,.0f} eval/s"
    )

    print(
        f"Delta rate:        "
        f"{delta_rate:,.0f} eval/s"
    )

    print()

    print(
        f"Prepared/position: "
        f"{prepared_speedup:.3f}x"
    )

    print(
        f"Delta/position:    "
        f"{delta_vs_position:.3f}x"
    )

    print(
        f"Delta/prepared:    "
        f"{delta_vs_prepared:.3f}x"
    )

    print()

    cache_size = len(
        prepared_delta_baseline
        .affected_indexes_cache
    )

    print(
        f"Delta cache size:  "
        f"{cache_size:,}"
    )


def main() -> None:
    parser = (
        argparse.ArgumentParser(
            description=(
                "Compare position-indexed, "
                "prepared-full, and "
                "prepared-delta transition "
                "evaluation."
            )
        )
    )

    parser.add_argument(
        "--iterations",
        type=int,
        default=100_000,
    )

    parser.add_argument(
        "--repeats",
        type=int,
        default=5,
    )

    args = (
        parser.parse_args()
    )

    layout = make_layout()

    statistics = (
        make_statistics()
    )

    evaluator = (
        FastLayoutScoreEvaluator(
            make_weights()
        )
    )

    (
        base_positions,
        cost_matrix,
    ) = build_integer_positions(
        evaluator,
        layout,
    )

    prepared = (
        evaluator
        .prepare_position_indexed_transitions(
            statistics
        )
    )

    prepared_delta_baseline = (
        evaluator
        .prepare_prepared_position_indexed_delta(
            base_positions,
            cost_matrix,
            prepared,
        )
    )

    for changed_count in range(
        5,
        11,
    ):
        (
            candidate,
            changed,
        ) = make_changed_letter_candidate(
            base_positions,
            changed_count,
        )

        run_case(
            title=(
                f"{changed_count} changed letters"
            ),
            evaluator=evaluator,
            candidate_positions=candidate,
            changed_indexes=changed,
            cost_matrix=cost_matrix,
            statistics=statistics,
            prepared=prepared,
            prepared_delta_baseline=(
                prepared_delta_baseline
            ),
            iterations=args.iterations,
            repeats=args.repeats,
        )

def make_changed_letter_candidate(
    base_positions: list[int],
    changed_count: int,
) -> tuple[
    list[int],
    tuple[int, ...],
]:
    """
    Create a candidate with exactly changed_count changed letters.

    The first five changed letters are vowels. Additional letters
    approximate consonants displaced during vowel-seed generation.
    """

    if not 2 <= changed_count <= 10:
        raise ValueError(
            "changed_count must be between 2 and 10"
        )

    letters = (
        "A",
        "E",
        "I",
        "O",
        "U",
        "B",
        "F",
        "J",
        "N",
        "V",
    )[:changed_count]

    changed = tuple(
        letter_index(letter)
        for letter in letters
    )

    candidate = list(
        base_positions
    )

    original_values = tuple(
        base_positions[index]
        for index in changed
    )

    rotated_values = (
        original_values[1:]
        + original_values[:1]
    )

    for (
        index,
        position,
    ) in zip(
        changed,
        rotated_values,
        strict=True,
    ):
        candidate[index] = position

    return (
        candidate,
        changed,
    )


if __name__ == "__main__":
    main()