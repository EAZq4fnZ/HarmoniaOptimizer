# evaluator/fast_layout_score_evaluator.py

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from models.enums import Hand
from models.layout import Layout
from models.logical_position import LogicalPosition
from models.logical_position_parser import LogicalPositionParser
from models.transition_cost import TransitionCostWeights

from .transition_statistics import TransitionStatistics

_FINGER_ORDER = {
    "PINKY": 0,
    "RING": 1,
    "MIDDLE": 2,
    "INDEX": 3,
}


@dataclass(frozen=True, slots=True)
class FastLayoutScore:
    """
    Minimal layout-evaluation result for exhaustive search.

    Unlike LayoutEvaluation, this object does not retain
    per-transition evaluation details.
    """

    total_cost: float
    evaluated_weight: float
    skipped_weight: float

@dataclass(frozen=True, slots=True)
class PreparedPositionIndexedTransitions:
    """
    Transition data prepared once for repeated position-indexed evaluation.

    records
        Only transitions whose source and target are valid A-Z indexes.
        Each record contains:

            (source_index, target_index, weighted_count)

        The raw transition count is intentionally omitted because the fast
        scoring path does not use it.

    permanently_skipped_weight
        Total weight of transitions that can never be evaluated by an A-Z
        indexed layout because either endpoint is outside A-Z.
    """

    records: tuple[tuple[int, int, float], ...]
    grouped_records: tuple[
        tuple[
            int,
            tuple[tuple[int, float], ...],
        ],
        ...,
    ]
    permanently_skipped_weight: float
    evaluated_weight: float


@dataclass(frozen=True, slots=True)
class PositionIndexedDeltaBaseline:
    """
    Baseline data for position-indexed delta evaluation.

    total_cost
        Full transition cost of the baseline layout.

    evaluated_weight
        Total weight of evaluated baseline transitions.

    skipped_weight
        Total weight skipped by the baseline layout.

    weighted_costs
        Weighted cost contribution of each transition record.

        Skipped transitions store 0.0.

    evaluated_weights
        Evaluated weight of each transition record.

        Evaluated transition:
            weighted_count

        Skipped transition:
            0.0
    """

    total_cost: float
    evaluated_weight: float
    skipped_weight: float

    weighted_costs: tuple[float, ...]
    evaluated_weights: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class PreparedPositionIndexedDeltaBaseline:
    """
    Baseline data for prepared position-indexed delta evaluation.

    The transition records use the same compact index space as
    PreparedPositionIndexedTransitions.records. Permanently invalid
    non-A-Z transitions are therefore excluded from the hot path and
    represented only by skipped_weight.

    affected_transition_bitsets_by_letter stores one Python integer
    bitset for each A-Z letter. Bit N is set when prepared record N
    involves that letter.

    affected_indexes_cache maps a 26-bit changed-letter mask to the
    compact tuple of affected prepared-record indexes. The cache is
    populated lazily and reused across exhaustive-search candidates.
    """

    total_cost: float
    evaluated_weight: float
    skipped_weight: float

    records: tuple[tuple[int, int, float], ...]
    weighted_costs: tuple[float, ...]
    evaluated_weights: tuple[float, ...]

    affected_transition_bitsets_by_letter: tuple[int, ...]
    affected_indexes_cache: dict[int, tuple[int, ...]]


class FastLayoutScoreEvaluator:
    """
    Fast transition-cost evaluator for exhaustive layout search.

    This evaluator preserves the scoring semantics of
    LayoutEvaluator while avoiding construction of detailed
    transition-evaluation objects.

    Four evaluation paths are provided:

        evaluate()
            Layout-based compatibility path.

        evaluate_mapping()
            Mapping-based exhaustive-search path.

        evaluate_indexed()
            A-Z indexed exhaustive-search path using string
            logical-position IDs.

        evaluate_position_indexed()
            Fully indexed exhaustive-search path using integer
            logical-position IDs and a precomputed cost matrix.

    The position-indexed path avoids both letter-key dictionary
    lookups and transition-cost dictionary lookups inside the
    hot transition loop.
    """

    def __init__(
        self,
        weights: TransitionCostWeights,
    ) -> None:
        self._weights = weights

        self._position_cache: dict[
            str,
            LogicalPosition,
        ] = {}

        self._transition_cost_cache: dict[
            tuple[str, str],
            float,
        ] = {}

    def evaluate(
        self,
        layout: Layout,
        statistics: TransitionStatistics,
    ) -> FastLayoutScore:
        """
        Evaluate one Layout using only aggregate transition values.
        """

        return self.evaluate_mapping(
            mapping=layout.mapping,
            statistics=statistics,
        )

    def evaluate_mapping(
        self,
        mapping: Mapping[str, str],
        statistics: TransitionStatistics,
    ) -> FastLayoutScore:
        """
        Evaluate a letter-to-position mapping directly.

        This avoids constructing a Layout during exhaustive search.

        The mapping is expected to use canonical uppercase
        character IDs, as Layout mappings do.
        """

        total_cost = 0.0
        evaluated_weight = 0.0
        skipped_weight = 0.0

        get_position = mapping.get

        cost_cache = self._transition_cost_cache
        get_cost = cost_cache.get

        for (
            source_id,
            target_id,
            _raw_count,
            weighted_count,
        ) in statistics.evaluation_records():
            source_position_id = get_position(
                source_id
            )

            target_position_id = get_position(
                target_id
            )

            if (
                source_position_id is None
                or target_position_id is None
            ):
                skipped_weight += weighted_count
                continue

            cache_key = (
                source_position_id,
                target_position_id,
            )

            cost = get_cost(
                cache_key
            )

            if cost is None:
                source_position = self._position(
                    source_position_id
                )

                target_position = self._position(
                    target_position_id
                )

                cost = self._calculate_cost(
                    source_position,
                    target_position,
                )

                cost_cache[
                    cache_key
                ] = cost

            total_cost += (
                cost
                * weighted_count
            )

            evaluated_weight += (
                weighted_count
            )

        return FastLayoutScore(
            total_cost=total_cost,
            evaluated_weight=evaluated_weight,
            skipped_weight=skipped_weight,
        )

    def evaluate_indexed(
        self,
        positions: Sequence[str | None],
        statistics: TransitionStatistics,
    ) -> FastLayoutScore:
        """
        Evaluate an A-Z indexed position sequence directly.

        positions must use:

            index 0  -> A
            index 1  -> B
            ...
            index 25 -> Z

        A None value means that the corresponding letter is not
        present in the layout.

        This path avoids mapping.get() for source and target letters
        inside the transition loop.
        """

        if len(positions) != 26:
            raise ValueError(
                "positions must contain exactly 26 entries"
            )

        total_cost = 0.0
        evaluated_weight = 0.0
        skipped_weight = 0.0

        cost_cache = self._transition_cost_cache
        get_cost = cost_cache.get

        for (
            source_index,
            target_index,
            _raw_count,
            weighted_count,
        ) in statistics.indexed_evaluation_records():
            if (
                source_index < 0
                or target_index < 0
            ):
                skipped_weight += weighted_count
                continue

            source_position_id = positions[
                source_index
            ]

            target_position_id = positions[
                target_index
            ]

            if (
                source_position_id is None
                or target_position_id is None
            ):
                skipped_weight += weighted_count
                continue

            cache_key = (
                source_position_id,
                target_position_id,
            )

            cost = get_cost(
                cache_key
            )

            if cost is None:
                source_position = self._position(
                    source_position_id
                )

                target_position = self._position(
                    target_position_id
                )

                cost = self._calculate_cost(
                    source_position,
                    target_position,
                )

                cost_cache[
                    cache_key
                ] = cost

            total_cost += (
                cost
                * weighted_count
            )

            evaluated_weight += (
                weighted_count
            )

        return FastLayoutScore(
            total_cost=total_cost,
            evaluated_weight=evaluated_weight,
            skipped_weight=skipped_weight,
        )

    def build_position_index(
        self,
        positions: Sequence[str],
    ) -> tuple[
        dict[str, int],
        tuple[tuple[float, ...], ...],
    ]:
        """
        Build an integer logical-position index and cost matrix.

        Returns:

            position_indexes
                Maps canonical logical-position IDs to integer IDs.

            cost_matrix
                cost_matrix[source][target] gives the transition
                cost directly.

        This method is intended to be called once before an
        exhaustive search.
        """

        unique_positions = tuple(
            dict.fromkeys(
                positions
            )
        )

        if not unique_positions:
            raise ValueError(
                "positions must not be empty"
            )

        position_indexes = {
            position_id: index
            for index, position_id
            in enumerate(unique_positions)
        }

        parsed_positions = tuple(
            self._position(
                position_id
            )
            for position_id in unique_positions
        )

        cost_matrix = tuple(
            tuple(
                self._calculate_cost(
                    source_position,
                    target_position,
                )
                for target_position
                in parsed_positions
            )
            for source_position
            in parsed_positions
        )

        return (
            position_indexes,
            cost_matrix,
        )

    def build_flat_position_costs(
        self,
        positions: Sequence[str],
    ) -> tuple[
        dict[str, int],
        tuple[float, ...],
        int,
    ]:
        """
        Build an integer logical-position index and flat cost table.

        Returns:

            position_indexes
                Logical-position string -> integer position ID.

            flat_costs
                Row-major flat transition-cost table.

                Cost lookup:

                    flat_costs[
                        source_position_index
                        * position_count
                        + target_position_index
                    ]

            position_count
                Number of indexed logical positions.

        This method is intended to be called once before exhaustive
        search.
        """

        unique_positions = tuple(
            dict.fromkeys(
                positions
            )
        )

        if not unique_positions:
            raise ValueError(
                "positions must not be empty"
            )

        position_indexes = {
            position_id: index
            for index, position_id
            in enumerate(
                unique_positions
            )
        }

        parsed_positions = tuple(
            self._position(
                position_id
            )
            for position_id
            in unique_positions
        )

        position_count = len(
            parsed_positions
        )

        flat_costs = tuple(
            self._calculate_cost(
                source_position,
                target_position,
            )
            for source_position
            in parsed_positions
            for target_position
            in parsed_positions
        )

        return (
            position_indexes,
            flat_costs,
            position_count,
        )

    def convert_to_position_indexes(
        self,
        positions: Sequence[str | None],
        position_indexes: Mapping[str, int],
    ) -> tuple[int, ...]:
        """
        Convert A-Z indexed string positions to integer position IDs.

        Missing positions are represented by -1.
        """

        if len(positions) != 26:
            raise ValueError(
                "positions must contain exactly 26 entries"
            )

        return tuple(
            (
                -1
                if position_id is None
                else position_indexes[
                    position_id
                ]
            )
            for position_id in positions
        )

    def evaluate_position_indexed(
        self,
        position_indexes: Sequence[int],
        cost_matrix: Sequence[
            Sequence[float]
        ],
        statistics: TransitionStatistics,
    ) -> FastLayoutScore:
        """
        Evaluate an A-Z indexed integer-position sequence.

        position_indexes must contain 26 entries:

            index 0  -> position ID for A
            index 1  -> position ID for B
            ...
            index 25 -> position ID for Z

        A negative position ID represents a missing letter.

        Unlike evaluate_indexed(), the hot loop performs no
        transition-cost dictionary lookup.
        """

        if len(position_indexes) != 26:
            raise ValueError(
                "position_indexes must contain exactly 26 entries"
            )

        total_cost = 0.0
        evaluated_weight = 0.0
        skipped_weight = 0.0

        positions = position_indexes
        matrix = cost_matrix

        for (
            source_index,
            target_index,
            _raw_count,
            weighted_count,
        ) in statistics.indexed_evaluation_records():
            if (
                source_index < 0
                or target_index < 0
            ):
                skipped_weight += weighted_count
                continue

            source_position_index = positions[
                source_index
            ]

            target_position_index = positions[
                target_index
            ]

            if (
                source_position_index < 0
                or target_position_index < 0
            ):
                skipped_weight += weighted_count
                continue

            cost = matrix[
                source_position_index
            ][
                target_position_index
            ]

            total_cost += (
                cost
                * weighted_count
            )

            evaluated_weight += (
                weighted_count
            )

        return FastLayoutScore(
            total_cost=total_cost,
            evaluated_weight=evaluated_weight,
            skipped_weight=skipped_weight,
        )

    def evaluate_position_indexed_flat(
        self,
        position_indexes: Sequence[int],
        flat_costs: Sequence[float],
        position_count: int,
        statistics: TransitionStatistics,
    ) -> FastLayoutScore:
        """
        Evaluate an A-Z indexed integer-position sequence using
        a flat row-major position-cost table.

        position_indexes must contain 26 entries.

        A negative position ID represents a missing letter.

        This path replaces:

            matrix[source][target]

        with:

            flat_costs[
                source * position_count + target
            ]

        inside the hot transition loop.
        """

        if len(position_indexes) != 26:
            raise ValueError(
                "position_indexes must contain exactly 26 entries"
            )

        if position_count <= 0:
            raise ValueError(
                "position_count must be greater than 0"
            )

        expected_cost_count = (
            position_count
            * position_count
        )

        if len(flat_costs) != expected_cost_count:
            raise ValueError(
                "flat_costs length does not match "
                "position_count"
            )

        total_cost = 0.0
        evaluated_weight = 0.0
        skipped_weight = 0.0

        positions = position_indexes
        costs = flat_costs
        count = position_count

        for (
            source_index,
            target_index,
            _raw_count,
            weighted_count,
        ) in statistics.indexed_evaluation_records():
            if (
                source_index < 0
                or target_index < 0
            ):
                skipped_weight += weighted_count
                continue

            source_position_index = positions[
                source_index
            ]

            target_position_index = positions[
                target_index
            ]

            if (
                source_position_index < 0
                or target_position_index < 0
            ):
                skipped_weight += weighted_count
                continue

            cost = costs[
                source_position_index
                * count
                + target_position_index
            ]

            total_cost += (
                cost
                * weighted_count
            )

            evaluated_weight += (
                weighted_count
            )

        return FastLayoutScore(
            total_cost=total_cost,
            evaluated_weight=evaluated_weight,
            skipped_weight=skipped_weight,
        )

    def prepare_position_indexed_transitions(
        self,
        statistics: TransitionStatistics,
    ) -> PreparedPositionIndexedTransitions:
        """
        Prepare transition records for repeated position-indexed evaluation.

        This method is intended to be called once before exhaustive search.
        It removes data and validity checks that do not depend on the
        candidate layout from the per-candidate hot loop.
        """

        records: list[tuple[int, int, float]] = []
        permanently_skipped_weight = 0.0
        evaluated_weight = 0.0

        append_record = records.append

        for (
            source_index,
            target_index,
            _raw_count,
            weighted_count,
        ) in statistics.indexed_evaluation_records():
            if (
                source_index < 0
                or target_index < 0
            ):
                permanently_skipped_weight += (
                    weighted_count
                )
                continue

            append_record(
                (
                    source_index,
                    target_index,
                    weighted_count,
                )
            )
            evaluated_weight += weighted_count

        grouped: list[list[tuple[int, float]]] = [
            [] for _ in range(26)
        ]

        for (
            source_index,
            target_index,
            weighted_count,
        ) in records:
            grouped[source_index].append(
                (
                    target_index,
                    weighted_count,
                )
            )

        grouped_records = tuple(
            (
                source_index,
                tuple(targets),
            )
            for source_index, targets in enumerate(grouped)
            if targets
        )

        return PreparedPositionIndexedTransitions(
            records=tuple(records),
            grouped_records=grouped_records,
            permanently_skipped_weight=(
                permanently_skipped_weight
            ),
            evaluated_weight=evaluated_weight,
        )

    def evaluate_prepared_position_indexed(
        self,
        position_indexes: Sequence[int],
        cost_matrix: Sequence[
            Sequence[float]
        ],
        prepared: PreparedPositionIndexedTransitions,
    ) -> FastLayoutScore:
        """
        Evaluate using transition records prepared before exhaustive search.

        Compared with evaluate_position_indexed(), this path avoids calling
        TransitionStatistics and avoids processing raw counts or permanently
        invalid transition endpoints for every candidate.
        """

        if len(position_indexes) != 26:
            raise ValueError(
                "position_indexes must contain exactly 26 entries"
            )

        total_cost = 0.0
        evaluated_weight = 0.0
        skipped_weight = (
            prepared.permanently_skipped_weight
        )

        positions = position_indexes
        matrix = cost_matrix

        for (
            source_index,
            target_index,
            weighted_count,
        ) in prepared.records:
            source_position_index = positions[
                source_index
            ]

            target_position_index = positions[
                target_index
            ]

            if (
                source_position_index < 0
                or target_position_index < 0
            ):
                skipped_weight += weighted_count
                continue

            total_cost += (
                matrix[
                    source_position_index
                ][
                    target_position_index
                ]
                * weighted_count
            )

            evaluated_weight += weighted_count

        return FastLayoutScore(
            total_cost=total_cost,
            evaluated_weight=evaluated_weight,
            skipped_weight=skipped_weight,
        )

    def evaluate_prepared_position_indexed_complete(
        self,
        position_indexes: Sequence[int],
        cost_matrix: Sequence[
            Sequence[float]
        ],
        prepared: PreparedPositionIndexedTransitions,
    ) -> FastLayoutScore:
        """
        Evaluate a complete A-Z position-indexed layout using prepared
        transition records.

        This is a specialized hot path for exhaustive searches where all
        26 letters are guaranteed to have valid position indexes.

        Unlike evaluate_prepared_position_indexed(), this method does not
        perform per-transition missing-letter checks.
        """

        if len(position_indexes) != 26:
            raise ValueError(
                "position_indexes must contain exactly 26 entries"
            )

        positions = position_indexes
        matrix = cost_matrix

        total_cost = 0.0

        for (
            source_index,
            targets,
        ) in prepared.grouped_records:
            source_row = matrix[
                positions[source_index]
            ]

            for (
                target_index,
                weighted_count,
            ) in targets:
                total_cost += (
                    source_row[
                        positions[target_index]
                    ]
                    * weighted_count
                )

        return FastLayoutScore(
            total_cost=total_cost,
            evaluated_weight=(
                prepared.evaluated_weight
            ),
            skipped_weight=(
                prepared.permanently_skipped_weight
            ),
        )

    def evaluate_prepared_position_indexed_complete_flat(
        self,
        position_indexes: Sequence[int],
        flat_costs: Sequence[float],
        position_count: int,
        prepared: PreparedPositionIndexedTransitions,
    ) -> FastLayoutScore:
        """
        Evaluate a complete A-Z position-indexed layout using prepared
        transition records and a flat row-major position-cost table.

        This is a specialized hot path for exhaustive searches where all
        26 letters are guaranteed to have valid position indexes.
        """

        if len(position_indexes) != 26:
            raise ValueError(
                "position_indexes must contain exactly 26 entries"
            )

        positions = position_indexes
        costs = flat_costs
        stride = position_count

        total_cost = 0.0

        for (
            source_index,
            target_index,
            weighted_count,
        ) in prepared.records:
            source_position_index = positions[
                source_index
            ]

            target_position_index = positions[
                target_index
            ]

            total_cost += (
                costs[
                    source_position_index
                    * stride
                    + target_position_index
                ]
                * weighted_count
            )

        return FastLayoutScore(
            total_cost=total_cost,
            evaluated_weight=(
                prepared.evaluated_weight
            ),
            skipped_weight=(
                prepared.permanently_skipped_weight
            ),
        )

    def prepare_prepared_position_indexed_delta(
        self,
        position_indexes: Sequence[int],
        cost_matrix: Sequence[
            Sequence[float]
        ],
        prepared: PreparedPositionIndexedTransitions,
    ) -> PreparedPositionIndexedDeltaBaseline:
        """
        Build a delta baseline from already-prepared transition records.

        Unlike prepare_position_indexed_delta(), this method operates in
        the compact PreparedPositionIndexedTransitions record space.

        It also prepares one integer transition bitset per A-Z letter.
        Later candidate evaluations can combine the relevant bitsets with
        fast integer OR operations instead of constructing and updating a
        Python set for every candidate.
        """

        if len(position_indexes) != 26:
            raise ValueError(
                "position_indexes must contain exactly 26 entries"
            )

        positions = position_indexes
        matrix = cost_matrix

        total_cost = 0.0
        evaluated_weight = 0.0
        skipped_weight = (
            prepared.permanently_skipped_weight
        )

        weighted_costs: list[float] = []
        evaluated_weights: list[float] = []

        affected_bitsets = [
            0
        ] * 26

        for (
            transition_index,
            record,
        ) in enumerate(
            prepared.records
        ):
            (
                source_index,
                target_index,
                weighted_count,
            ) = record

            transition_bit = (
                1 << transition_index
            )

            affected_bitsets[
                source_index
            ] |= transition_bit

            if target_index != source_index:
                affected_bitsets[
                    target_index
                ] |= transition_bit

            source_position_index = positions[
                source_index
            ]

            target_position_index = positions[
                target_index
            ]

            if (
                source_position_index < 0
                or target_position_index < 0
            ):
                skipped_weight += weighted_count

                weighted_costs.append(
                    0.0
                )

                evaluated_weights.append(
                    0.0
                )

                continue

            weighted_cost = (
                matrix[
                    source_position_index
                ][
                    target_position_index
                ]
                * weighted_count
            )

            total_cost += weighted_cost
            evaluated_weight += weighted_count

            weighted_costs.append(
                weighted_cost
            )

            evaluated_weights.append(
                weighted_count
            )

        return PreparedPositionIndexedDeltaBaseline(
            total_cost=total_cost,
            evaluated_weight=evaluated_weight,
            skipped_weight=skipped_weight,
            records=prepared.records,
            weighted_costs=tuple(
                weighted_costs
            ),
            evaluated_weights=tuple(
                evaluated_weights
            ),
            affected_transition_bitsets_by_letter=tuple(
                affected_bitsets
            ),
            affected_indexes_cache={},
        )

    def evaluate_prepared_position_indexed_delta(
        self,
        position_indexes: Sequence[int],
        cost_matrix: Sequence[
            Sequence[float]
        ],
        baseline: PreparedPositionIndexedDeltaBaseline,
        changed_letter_indexes: Sequence[int],
    ) -> FastLayoutScore:
        """
        Evaluate a candidate using the prepared delta baseline.

        Only transitions involving changed letters are recalculated.

        The affected transition indexes are obtained without per-candidate
        set construction. A 26-bit changed-letter mask is used as a cache
        key, while precomputed integer transition bitsets are ORed together
        only on the first occurrence of a changed-letter combination.
        """

        if len(position_indexes) != 26:
            raise ValueError(
                "position_indexes must contain exactly 26 entries"
            )

        if not changed_letter_indexes:
            return FastLayoutScore(
                total_cost=baseline.total_cost,
                evaluated_weight=(
                    baseline.evaluated_weight
                ),
                skipped_weight=baseline.skipped_weight,
            )

        changed_mask = 0

        for letter_index in changed_letter_indexes:
            if not 0 <= letter_index < 26:
                raise ValueError(
                    "changed letter indexes must "
                    "be between 0 and 25"
                )

            changed_mask |= (
                1 << letter_index
            )

        affected_indexes = (
            baseline
            .affected_indexes_cache
            .get(
                changed_mask
            )
        )

        if affected_indexes is None:
            affected_bits = 0

            bitsets_by_letter = (
                baseline
                .affected_transition_bitsets_by_letter
            )

            remaining_mask = changed_mask

            while remaining_mask:
                lowest_bit = (
                    remaining_mask
                    & -remaining_mask
                )

                letter_index = (
                    lowest_bit.bit_length()
                    - 1
                )

                affected_bits |= (
                    bitsets_by_letter[
                        letter_index
                    ]
                )

                remaining_mask ^= (
                    lowest_bit
                )

            mutable_indexes: list[int] = []
            append_index = mutable_indexes.append

            while affected_bits:
                lowest_bit = (
                    affected_bits
                    & -affected_bits
                )

                append_index(
                    lowest_bit.bit_length()
                    - 1
                )

                affected_bits ^= (
                    lowest_bit
                )

            affected_indexes = tuple(
                mutable_indexes
            )

            baseline.affected_indexes_cache[
                changed_mask
            ] = affected_indexes

        positions = position_indexes
        matrix = cost_matrix
        records = baseline.records

        baseline_weighted_costs = (
            baseline.weighted_costs
        )

        baseline_evaluated_weights = (
            baseline.evaluated_weights
        )

        total_cost = baseline.total_cost
        evaluated_weight = (
            baseline.evaluated_weight
        )
        skipped_weight = (
            baseline.skipped_weight
        )

        for transition_index in affected_indexes:
            (
                source_index,
                target_index,
                weighted_count,
            ) = records[
                transition_index
            ]

            old_weighted_cost = (
                baseline_weighted_costs[
                    transition_index
                ]
            )

            old_evaluated_weight = (
                baseline_evaluated_weights[
                    transition_index
                ]
            )

            source_position_index = positions[
                source_index
            ]

            target_position_index = positions[
                target_index
            ]

            if (
                source_position_index < 0
                or target_position_index < 0
            ):
                new_weighted_cost = 0.0
                new_evaluated_weight = 0.0

            else:
                new_weighted_cost = (
                    matrix[
                        source_position_index
                    ][
                        target_position_index
                    ]
                    * weighted_count
                )

                new_evaluated_weight = (
                    weighted_count
                )

            total_cost += (
                new_weighted_cost
                - old_weighted_cost
            )

            evaluated_weight += (
                new_evaluated_weight
                - old_evaluated_weight
            )

            skipped_weight += (
                old_evaluated_weight
                - new_evaluated_weight
            )

        return FastLayoutScore(
            total_cost=total_cost,
            evaluated_weight=evaluated_weight,
            skipped_weight=skipped_weight,
        )

    def prepare_position_indexed_delta(
        self,
        position_indexes: Sequence[int],
        cost_matrix: Sequence[
            Sequence[float]
        ],
        statistics: TransitionStatistics,
    ) -> PositionIndexedDeltaBaseline:
        """
        Build baseline data for repeated delta evaluation.

        This method performs one complete transition evaluation.

        Later candidates can then be evaluated by recalculating
        only transitions involving letters whose positions changed.
        """

        if len(position_indexes) != 26:
            raise ValueError(
                "position_indexes must contain exactly 26 entries"
            )

        positions = position_indexes
        matrix = cost_matrix

        total_cost = 0.0
        evaluated_weight = 0.0
        skipped_weight = 0.0

        weighted_costs: list[float] = []
        evaluated_weights: list[float] = []

        for (
            source_index,
            target_index,
            _raw_count,
            weighted_count,
        ) in statistics.indexed_evaluation_records():
            if (
                source_index < 0
                or target_index < 0
            ):
                skipped_weight += weighted_count

                weighted_costs.append(
                    0.0
                )

                evaluated_weights.append(
                    0.0
                )

                continue

            source_position_index = positions[
                source_index
            ]

            target_position_index = positions[
                target_index
            ]

            if (
                source_position_index < 0
                or target_position_index < 0
            ):
                skipped_weight += weighted_count

                weighted_costs.append(
                    0.0
                )

                evaluated_weights.append(
                    0.0
                )

                continue

            weighted_cost = (
                matrix[
                    source_position_index
                ][
                    target_position_index
                ]
                * weighted_count
            )

            total_cost += weighted_cost
            evaluated_weight += weighted_count

            weighted_costs.append(
                weighted_cost
            )

            evaluated_weights.append(
                weighted_count
            )

        return PositionIndexedDeltaBaseline(
            total_cost=total_cost,
            evaluated_weight=evaluated_weight,
            skipped_weight=skipped_weight,
            weighted_costs=tuple(
                weighted_costs
            ),
            evaluated_weights=tuple(
                evaluated_weights
            ),
        )

    def evaluate_position_indexed_delta(
        self,
        position_indexes: Sequence[int],
        cost_matrix: Sequence[
            Sequence[float]
        ],
        statistics: TransitionStatistics,
        baseline: PositionIndexedDeltaBaseline,
        changed_letter_indexes: Sequence[int],
    ) -> FastLayoutScore:
        """
        Evaluate a candidate from a prepared baseline.

        Only transitions involving letters in
        changed_letter_indexes are recalculated.

        All unaffected transition contributions are reused from
        the baseline.
        """

        if len(position_indexes) != 26:
            raise ValueError(
                "position_indexes must contain exactly 26 entries"
            )

        if not changed_letter_indexes:
            return FastLayoutScore(
                total_cost=baseline.total_cost,
                evaluated_weight=(
                    baseline.evaluated_weight
                ),
                skipped_weight=baseline.skipped_weight,
            )

        records = (
            statistics.indexed_evaluation_records()
        )

        affected_by_letter = (
            statistics
            .affected_transition_indexes_by_letter()
        )

        affected_indexes: set[int] = set()

        for letter_index in changed_letter_indexes:
            if not 0 <= letter_index < 26:
                raise ValueError(
                    "changed letter indexes must "
                    "be between 0 and 25"
                )

            affected_indexes.update(
                affected_by_letter[
                    letter_index
                ]
            )

        positions = position_indexes
        matrix = cost_matrix

        total_cost = baseline.total_cost
        evaluated_weight = (
            baseline.evaluated_weight
        )
        skipped_weight = (
            baseline.skipped_weight
        )

        baseline_weighted_costs = (
            baseline.weighted_costs
        )

        baseline_evaluated_weights = (
            baseline.evaluated_weights
        )

        for transition_index in affected_indexes:
            (
                source_index,
                target_index,
                _raw_count,
                weighted_count,
            ) = records[
                transition_index
            ]

            old_weighted_cost = (
                baseline_weighted_costs[
                    transition_index
                ]
            )

            old_evaluated_weight = (
                baseline_evaluated_weights[
                    transition_index
                ]
            )

            if (
                source_index < 0
                or target_index < 0
            ):
                new_weighted_cost = 0.0
                new_evaluated_weight = 0.0

            else:
                source_position_index = (
                    positions[
                        source_index
                    ]
                )

                target_position_index = (
                    positions[
                        target_index
                    ]
                )

                if (
                    source_position_index < 0
                    or target_position_index < 0
                ):
                    new_weighted_cost = 0.0
                    new_evaluated_weight = 0.0

                else:
                    new_weighted_cost = (
                        matrix[
                            source_position_index
                        ][
                            target_position_index
                        ]
                        * weighted_count
                    )

                    new_evaluated_weight = (
                        weighted_count
                    )

            total_cost += (
                new_weighted_cost
                - old_weighted_cost
            )

            evaluated_weight += (
                new_evaluated_weight
                - old_evaluated_weight
            )

            skipped_weight += (
                old_evaluated_weight
                - new_evaluated_weight
            )

        return FastLayoutScore(
            total_cost=total_cost,
            evaluated_weight=evaluated_weight,
            skipped_weight=skipped_weight,
        )

    def _position(
        self,
        position_id: str,
    ) -> LogicalPosition:
        """
        Return a cached parsed logical position.
        """

        position = self._position_cache.get(
            position_id
        )

        if position is None:
            position = LogicalPositionParser.parse(
                position_id
            )

            self._position_cache[
                position_id
            ] = position

        return position

    def _calculate_cost(
        self,
        source: LogicalPosition,
        target: LogicalPosition,
    ) -> float:
        """
        Calculate transition cost directly from two positions.

        The formula intentionally mirrors:

        TransitionEvaluator
            -> TransitionCostEvaluator
        """

        same_hand = (
            source.hand
            == target.hand
        )

        same_finger = (
            same_hand
            and source.finger
            == target.finger
        )

        same_row = (
            source.row
            == target.row
        )

        cost = 0.0

        if same_finger:
            cost += (
                self._weights.same_finger_penalty
            )

        if same_hand:
            cost += (
                self._weights.same_hand_penalty
            )
        else:
            cost -= (
                self._weights.alternation_reward
            )

        if not same_row:
            cost += (
                self._weights.row_change_penalty
            )

        if same_hand and not same_finger:
            source_index = _FINGER_ORDER[
                source.finger.name
            ]

            target_index = _FINGER_ORDER[
                target.finger.name
            ]

            difference = (
                target_index
                - source_index
            )

            if abs(difference) == 1:
                if source.hand is Hand.LEFT:
                    inward = (
                        difference == 1
                    )
                else:
                    inward = (
                        difference == -1
                    )

                if inward:
                    cost -= (
                        self
                        ._weights
                        .inward_roll_reward
                    )
                else:
                    cost -= (
                        self
                        ._weights
                        .outward_roll_reward
                    )

        return cost

