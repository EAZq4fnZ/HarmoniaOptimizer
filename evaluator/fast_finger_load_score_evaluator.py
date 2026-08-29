# evaluator/fast_finger_load_score_evaluator.py

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from models.enums import Finger, Hand
from models.finger_load_budget import FingerLoadBudget
from models.layout import Layout
from models.logical_position_parser import LogicalPositionParser

from .character_statistics import CharacterStatistics


@dataclass(frozen=True, slots=True)
class PreparedPositionIndexedFingerLoadBaseline:
    """
    Baseline finger-load data for complete position-indexed delta evaluation.
    """

    finger_loads: tuple[float, ...]
    total_weighted_load: float


class FastFingerLoadScoreEvaluator:
    """
    Calculate only the aggregate finger-load penalty required
    for candidate scoring.

    Unlike FingerLoadPipeline, this evaluator does not create
    FingerLoad or FingerLoadEvaluation objects.

    Several evaluation paths are provided:

        evaluate()
            Layout-based compatibility path.

        evaluate_mapping()
            Mapping-based exhaustive-search path.

        evaluate_indexed()
            A-Z indexed path using string logical-position IDs.

        evaluate_position_indexed()
            Fully indexed path using integer logical-position IDs.

    The position-indexed path avoids logical-position string
    dictionary lookups inside the hot character loop.
    """

    LETTER_COUNT = 26
    A_ORD = ord("A")

    def __init__(
        self,
        budgets: tuple[FingerLoadBudget, ...],
    ) -> None:
        self._budgets = budgets

        self._position_pair_cache: dict[
            str,
            tuple[Hand, Finger],
        ] = {}

        self._allowed_ratio_map: dict[
            tuple[Hand, Finger],
            float,
        ] = {
            (
                budget.hand,
                budget.finger,
            ): (
                budget.target_ratio
                + budget.tolerance
            )
            for budget in budgets
        }

        self._weighted_statistics_cache: dict[
            int,
            tuple[float, ...],
        ] = {}

    def evaluate(
        self,
        layout: Layout,
        statistics: CharacterStatistics,
    ) -> float:
        """
        Evaluate one Layout and return only the total penalty.
        """

        return self.evaluate_mapping(
            mapping=layout.mapping,
            statistics=statistics,
        )

    def evaluate_mapping(
        self,
        mapping: Mapping[str, str],
        statistics: CharacterStatistics,
    ) -> float:
        """
        Evaluate a letter-to-position mapping directly.

        This avoids constructing a Layout during exhaustive search.
        """

        weighted_statistics = (
            statistics.weighted()
        )

        weighted_loads: dict[
            tuple[Hand, Finger],
            float,
        ] = {}

        total_weighted_load = 0.0

        get_position = mapping.get
        get_pair = self._position_pair_cache.get

        for (
            character,
            weighted_count,
        ) in weighted_statistics.items():
            character_id = character.upper()

            position_id = get_position(
                character_id
            )

            if position_id is None:
                continue

            pair = get_pair(
                position_id
            )

            if pair is None:
                pair = self._pair(
                    position_id
                )

            weighted_loads[pair] = (
                weighted_loads.get(
                    pair,
                    0.0,
                )
                + weighted_count
            )

            total_weighted_load += (
                weighted_count
            )

        return self._calculate_penalty(
            weighted_loads=weighted_loads,
            total_weighted_load=total_weighted_load,
        )

    def evaluate_indexed(
        self,
        positions: Sequence[str],
        statistics: CharacterStatistics,
    ) -> float:
        """
        Evaluate positions indexed by alphabet position.

        positions[0]  -> A
        positions[1]  -> B
        ...
        positions[25] -> Z

        Only characters A-Z contribute, matching the behavior of
        evaluate_mapping() for a normal 26-letter layout.
        """

        if len(positions) != self.LETTER_COUNT:
            raise ValueError(
                "positions must contain exactly 26 entries"
            )

        weighted_statistics = (
            self._indexed_weighted_statistics(
                statistics
            )
        )

        weighted_loads: dict[
            tuple[Hand, Finger],
            float,
        ] = {}

        total_weighted_load = 0.0

        get_pair = self._position_pair_cache.get
        get_load = weighted_loads.get

        for index, weighted_count in enumerate(
            weighted_statistics
        ):
            if weighted_count == 0.0:
                continue

            position_id = positions[index]

            pair = get_pair(
                position_id
            )

            if pair is None:
                pair = self._pair(
                    position_id
                )

            weighted_loads[pair] = (
                get_load(
                    pair,
                    0.0,
                )
                + weighted_count
            )

            total_weighted_load += (
                weighted_count
            )

        return self._calculate_penalty(
            weighted_loads=weighted_loads,
            total_weighted_load=total_weighted_load,
        )

    def build_position_finger_index(
        self,
        positions: Sequence[str],
        position_indexes: Mapping[str, int],
    ) -> tuple[
        tuple[int, ...],
        tuple[float, ...],
    ]:
        """
        Build position-index -> finger-slot lookup data.

        position_indexes must use the same integer logical-position
        IDs as FastLayoutScoreEvaluator.build_position_index().

        Returns:

            position_finger_indexes
                position_finger_indexes[position_index] gives the
                integer finger-load slot for that logical position.

            allowed_ratios
                allowed_ratios[finger_slot] gives the maximum
                permitted load ratio for that slot.

        Hand/finger pairs without an explicit budget still receive
        a slot. Their allowed ratio is 1.0, so they cannot produce
        an excess-load penalty.
        """

        if not positions:
            raise ValueError(
                "positions must not be empty"
            )

        position_count = len(
            position_indexes
        )

        if position_count == 0:
            raise ValueError(
                "position_indexes must not be empty"
            )

        pair_indexes: dict[
            tuple[Hand, Finger],
            int,
        ] = {}

        position_finger_indexes = [
            -1
        ] * position_count

        for position_id in positions:
            position_index = position_indexes[
                position_id
            ]

            pair = self._position_pair_cache.get(
                position_id
            )

            if pair is None:
                pair = self._pair(
                    position_id
                )

            pair_index = pair_indexes.get(
                pair
            )

            if pair_index is None:
                pair_index = len(
                    pair_indexes
                )

                pair_indexes[pair] = (
                    pair_index
                )

            position_finger_indexes[
                position_index
            ] = pair_index

        allowed_ratios = [
            1.0
        ] * len(pair_indexes)

        for pair, pair_index in pair_indexes.items():
            allowed_ratio = (
                self._allowed_ratio_map.get(
                    pair
                )
            )

            if allowed_ratio is not None:
                allowed_ratios[
                    pair_index
                ] = allowed_ratio

        if any(
            pair_index < 0
            for pair_index
            in position_finger_indexes
        ):
            raise ValueError(
                "position_indexes contains positions "
                "not present in positions"
            )

        return (
            tuple(position_finger_indexes),
            tuple(allowed_ratios),
        )

    def evaluate_position_indexed(
        self,
        positions: Sequence[int],
        position_finger_indexes: Sequence[int],
        allowed_ratios: Sequence[float],
        statistics: CharacterStatistics,
    ) -> float:
        """
        Evaluate A-Z indexed integer logical-position IDs.

        positions must use:

            positions[0]  -> integer position ID for A
            positions[1]  -> integer position ID for B
            ...
            positions[25] -> integer position ID for Z

        position_finger_indexes maps each integer position ID
        directly to a compact hand/finger slot.

        No logical-position string dictionary lookup is performed
        inside the hot character loop.
        """

        if len(positions) != self.LETTER_COUNT:
            raise ValueError(
                "positions must contain exactly 26 entries"
            )

        weighted_statistics = (
            self._indexed_weighted_statistics(
                statistics
            )
        )

        finger_loads = [
            0.0
        ] * len(allowed_ratios)

        total_weighted_load = 0.0

        finger_indexes = (
            position_finger_indexes
        )

        for index, weighted_count in enumerate(
            weighted_statistics
        ):
            if weighted_count == 0.0:
                continue

            position_index = positions[
                index
            ]

            if position_index < 0:
                continue

            finger_index = finger_indexes[
                position_index
            ]

            finger_loads[
                finger_index
            ] += weighted_count

            total_weighted_load += (
                weighted_count
            )

        if total_weighted_load <= 0.0:
            return 0.0

        total_penalty = 0.0

        for finger_index, allowed_ratio in enumerate(
            allowed_ratios
        ):
            actual_ratio = (
                finger_loads[
                    finger_index
                ]
                / total_weighted_load
            )

            excess_ratio = (
                actual_ratio
                - allowed_ratio
            )

            if excess_ratio > 0.0:
                total_penalty += (
                    excess_ratio
                )

        return total_penalty

    def prepare_position_indexed_statistics(
        self,
        statistics: CharacterStatistics,
    ) -> tuple[
        tuple[float, ...],
        float,
    ]:
        """
        Prepare immutable A-Z weighted character statistics for
        repeated complete position-indexed evaluation.

        The total weighted load is calculated once outside the
        exhaustive candidate loop.
        """

        weighted_statistics = (
            self._indexed_weighted_statistics(
                statistics
            )
        )

        return (
            weighted_statistics,
            sum(weighted_statistics),
        )

    def evaluate_prepared_position_indexed_complete(
        self,
        positions: Sequence[int],
        position_finger_indexes: Sequence[int],
        allowed_ratios: Sequence[float],
        weighted_statistics: Sequence[float],
        total_weighted_load: float,
    ) -> float:
        """
        Evaluate a complete A-Z position-indexed layout using
        precomputed character statistics.

        This specialized hot path assumes every A-Z entry in
        positions contains a valid non-negative position index.
        """

        if len(positions) != self.LETTER_COUNT:
            raise ValueError(
                "positions must contain exactly 26 entries"
            )

        if len(weighted_statistics) != self.LETTER_COUNT:
            raise ValueError(
                "weighted_statistics must contain exactly 26 entries"
            )

        if total_weighted_load <= 0.0:
            return 0.0

        finger_loads = [
            0.0
        ] * len(allowed_ratios)

        finger_indexes = (
            position_finger_indexes
        )

        for index, weighted_count in enumerate(
            weighted_statistics
        ):
            if weighted_count == 0.0:
                continue

            finger_index = finger_indexes[
                positions[index]
            ]

            finger_loads[
                finger_index
            ] += weighted_count

        inverse_total_weighted_load = (
            1.0
            / total_weighted_load
        )

        total_penalty = 0.0

        for finger_index, allowed_ratio in enumerate(
            allowed_ratios
        ):
            actual_ratio = (
                finger_loads[
                    finger_index
                ]
                * inverse_total_weighted_load
            )

            excess_ratio = (
                actual_ratio
                - allowed_ratio
            )

            if excess_ratio > 0.0:
                total_penalty += (
                    excess_ratio
                )

        return total_penalty

    def prepare_position_indexed_complete_delta_baseline(
        self,
        positions: Sequence[int],
        position_finger_indexes: Sequence[int],
        allowed_ratios: Sequence[float],
        weighted_statistics: Sequence[float],
        total_weighted_load: float,
    ) -> PreparedPositionIndexedFingerLoadBaseline:
        """
        Build baseline finger loads once for repeated complete-layout delta
        evaluation.

        This method assumes every A-Z entry in positions contains a valid
        non-negative position index.
        """

        if len(positions) != self.LETTER_COUNT:
            raise ValueError(
                "positions must contain exactly 26 entries"
            )

        if len(weighted_statistics) != self.LETTER_COUNT:
            raise ValueError(
                "weighted_statistics must contain exactly 26 entries"
            )

        finger_loads = [
            0.0
        ] * len(allowed_ratios)

        finger_indexes = position_finger_indexes

        for index, weighted_count in enumerate(
            weighted_statistics
        ):
            if weighted_count == 0.0:
                continue

            finger_index = finger_indexes[
                positions[index]
            ]

            finger_loads[
                finger_index
            ] += weighted_count

        return PreparedPositionIndexedFingerLoadBaseline(
            finger_loads=tuple(finger_loads),
            total_weighted_load=total_weighted_load,
        )

    def prepare_position_indexed_complete_vowel_group_baseline(
        self,
        positions: Sequence[int],
        position_finger_indexes: Sequence[int],
        weighted_statistics: Sequence[float],
        total_weighted_load: float,
    ) -> PreparedPositionIndexedFingerLoadBaseline:
        """
        Build a position-set-local finger-load baseline containing consonants.

        Within one selected five-position vowel set, consonant positions are
        fixed across all 5! vowel permutations. Preparing their loads once
        lets the per-permutation hot path add only A/E/I/O/U.
        """

        if len(positions) != self.LETTER_COUNT:
            raise ValueError(
                "positions must contain exactly 26 entries"
            )

        if len(weighted_statistics) != self.LETTER_COUNT:
            raise ValueError(
                "weighted_statistics must contain exactly 26 entries"
            )

        finger_count = (
            max(position_finger_indexes) + 1
            if position_finger_indexes
            else 0
        )
        finger_loads = [0.0] * finger_count
        finger_indexes = position_finger_indexes
        vowel_indexes = (0, 4, 8, 14, 20)

        for letter_index, weighted_count in enumerate(
            weighted_statistics
        ):
            if (
                letter_index in vowel_indexes
                or weighted_count == 0.0
            ):
                continue

            finger_loads[
                finger_indexes[positions[letter_index]]
            ] += weighted_count

        return PreparedPositionIndexedFingerLoadBaseline(
            finger_loads=tuple(finger_loads),
            total_weighted_load=total_weighted_load,
        )

    def evaluate_prepared_position_indexed_complete_vowel_group(
        self,
        positions: Sequence[int],
        position_finger_indexes: Sequence[int],
        allowed_ratios: Sequence[float],
        weighted_statistics: Sequence[float],
        baseline: PreparedPositionIndexedFingerLoadBaseline,
    ) -> float:
        """
        Evaluate one vowel permutation from a position-set-local baseline.

        The baseline already contains every consonant load. Only the five
        vowel loads vary across permutations in the same selected position
        set.
        """

        total_weighted_load = baseline.total_weighted_load

        if total_weighted_load <= 0.0:
            return 0.0

        finger_loads = list(baseline.finger_loads)
        finger_indexes = position_finger_indexes
        weighted = weighted_statistics

        finger_loads[
            finger_indexes[positions[0]]
        ] += weighted[0]
        finger_loads[
            finger_indexes[positions[4]]
        ] += weighted[4]
        finger_loads[
            finger_indexes[positions[8]]
        ] += weighted[8]
        finger_loads[
            finger_indexes[positions[14]]
        ] += weighted[14]
        finger_loads[
            finger_indexes[positions[20]]
        ] += weighted[20]

        inverse_total_weighted_load = (
            1.0 / total_weighted_load
        )
        total_penalty = 0.0

        for finger_index, allowed_ratio in enumerate(
            allowed_ratios
        ):
            actual_ratio = (
                finger_loads[finger_index]
                * inverse_total_weighted_load
            )
            excess_ratio = actual_ratio - allowed_ratio

            if excess_ratio > 0.0:
                total_penalty += excess_ratio

        return total_penalty

    def evaluate_prepared_position_indexed_complete_delta(
        self,
        baseline_positions: Sequence[int],
        positions: Sequence[int],
        position_finger_indexes: Sequence[int],
        allowed_ratios: Sequence[float],
        weighted_statistics: Sequence[float],
        baseline: PreparedPositionIndexedFingerLoadBaseline,
        changed_letter_indexes: Sequence[int],
    ) -> float:
        """
        Evaluate finger-load penalty by applying only changed-letter movement
        to a prepared baseline.

        baseline_positions and positions use the same A-Z integer letter
        index space. changed_letter_indexes contains only letters whose
        logical positions may differ from baseline_positions.

        The total weighted character load is invariant across complete
        layouts, so only per-finger weighted loads need delta updates.
        """

        if len(baseline_positions) != self.LETTER_COUNT:
            raise ValueError(
                "baseline_positions must contain exactly 26 entries"
            )

        if len(positions) != self.LETTER_COUNT:
            raise ValueError(
                "positions must contain exactly 26 entries"
            )

        if len(weighted_statistics) != self.LETTER_COUNT:
            raise ValueError(
                "weighted_statistics must contain exactly 26 entries"
            )

        total_weighted_load = baseline.total_weighted_load

        if total_weighted_load <= 0.0:
            return 0.0

        finger_loads = list(
            baseline.finger_loads
        )

        finger_indexes = position_finger_indexes
        base_positions = baseline_positions
        candidate_positions = positions
        weighted = weighted_statistics

        for letter_index in changed_letter_indexes:
            weighted_count = weighted[
                letter_index
            ]

            if weighted_count == 0.0:
                continue

            old_position_index = base_positions[
                letter_index
            ]
            new_position_index = candidate_positions[
                letter_index
            ]

            if old_position_index == new_position_index:
                continue

            old_finger_index = finger_indexes[
                old_position_index
            ]
            new_finger_index = finger_indexes[
                new_position_index
            ]

            if old_finger_index == new_finger_index:
                continue

            finger_loads[
                old_finger_index
            ] -= weighted_count

            finger_loads[
                new_finger_index
            ] += weighted_count

        inverse_total_weighted_load = (
            1.0
            / total_weighted_load
        )

        total_penalty = 0.0

        for finger_index, allowed_ratio in enumerate(
            allowed_ratios
        ):
            actual_ratio = (
                finger_loads[
                    finger_index
                ]
                * inverse_total_weighted_load
            )

            excess_ratio = (
                actual_ratio
                - allowed_ratio
            )

            if excess_ratio > 0.0:
                total_penalty += (
                    excess_ratio
                )

        return total_penalty

    def _indexed_weighted_statistics(
        self,
        statistics: CharacterStatistics,
    ) -> tuple[float, ...]:
        """
        Return cached A-Z weighted counts for CharacterStatistics.

        The cache is keyed by object identity. CharacterStatistics
        is treated as immutable during an exhaustive evaluation run.
        """

        cache_key = id(
            statistics
        )

        cached = (
            self
            ._weighted_statistics_cache
            .get(cache_key)
        )

        if cached is not None:
            return cached

        counts = [
            0.0
        ] * self.LETTER_COUNT

        for (
            character,
            weighted_count,
        ) in statistics.weighted().items():
            character_id = character.upper()

            if len(character_id) != 1:
                continue

            index = (
                ord(character_id)
                - self.A_ORD
            )

            if (
                0
                <= index
                < self.LETTER_COUNT
            ):
                counts[index] += (
                    weighted_count
                )

        result = tuple(
            counts
        )

        self._weighted_statistics_cache[
            cache_key
        ] = result

        return result

    def _pair(
        self,
        position_id: str,
    ) -> tuple[Hand, Finger]:
        """
        Return the cached hand/finger pair for a position.
        """

        position = (
            LogicalPositionParser.parse(
                position_id
            )
        )

        pair = (
            position.hand,
            position.finger,
        )

        self._position_pair_cache[
            position_id
        ] = pair

        return pair

    def _calculate_penalty(
        self,
        *,
        weighted_loads: Mapping[
            tuple[Hand, Finger],
            float,
        ],
        total_weighted_load: float,
    ) -> float:
        """
        Calculate aggregate excess-load penalty.
        """

        if total_weighted_load <= 0.0:
            return 0.0

        total_penalty = 0.0

        get_load = weighted_loads.get

        for (
            pair,
            allowed_ratio,
        ) in self._allowed_ratio_map.items():
            weighted_count = get_load(
                pair,
                0.0,
            )

            actual_ratio = (
                weighted_count
                / total_weighted_load
            )

            excess_ratio = (
                actual_ratio
                - allowed_ratio
            )

            if excess_ratio > 0.0:
                total_penalty += (
                    excess_ratio
                )

        return total_penalty