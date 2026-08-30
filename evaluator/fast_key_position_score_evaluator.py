from __future__ import annotations

from collections.abc import Mapping, Sequence

from evaluator.character_statistics import CharacterStatistics
from models.key_position_cost import KeyPositionCostProfile
from models.layout import Layout


class FastKeyPositionScoreEvaluator:
    """
    Calculate only the normalized unigram key-position score.

    Lower score is better.
    """

    LETTER_COUNT = 26
    A_ORD = ord("A")

    def __init__(
        self,
        profile: KeyPositionCostProfile,
    ) -> None:
        self._profile = profile

        self._weighted_statistics_cache: dict[
            int,
            tuple[float, ...],
        ] = {}

    def evaluate(
        self,
        layout: Layout,
        statistics: CharacterStatistics,
    ) -> float:
        return self.evaluate_mapping(
            layout.mapping,
            statistics,
        )

    def evaluate_mapping(
        self,
        mapping: Mapping[str, str],
        statistics: CharacterStatistics,
    ) -> float:
        total_cost = 0.0
        evaluated_weight = 0.0

        for character, weighted_count in (
            statistics.weighted().items()
        ):
            character_id = character.upper()

            position_id = mapping.get(
                character_id
            )

            if position_id is None:
                continue

            position_cost = self._profile.cost(
                position_id
            )

            if position_cost is None:
                continue

            total_cost += (
                position_cost
                * weighted_count
            )
            evaluated_weight += weighted_count

        if evaluated_weight <= 0.0:
            return 0.0

        return (
            total_cost
            / evaluated_weight
        )

    def prepare_position_indexed_statistics(
        self,
        statistics: CharacterStatistics,
    ) -> tuple[
        tuple[float, ...],
        float,
    ]:
        weighted_statistics = (
            self._indexed_weighted_statistics(
                statistics
            )
        )

        return (
            weighted_statistics,
            sum(weighted_statistics),
        )

    def build_position_costs(
        self,
        positions: Sequence[str],
    ) -> tuple[float, ...]:
        """
        Build costs indexed by integer logical-position ID.

        Every supplied position must exist in the profile.
        """

        result: list[float] = []

        for position_id in positions:
            position_cost = self._profile.cost(
                position_id
            )

            if position_cost is None:
                raise ValueError(
                    "missing key position cost for "
                    f"{position_id!r}"
                )

            result.append(position_cost)

        return tuple(result)

    def evaluate_prepared_position_indexed_complete(
        self,
        positions: Sequence[int],
        position_costs: Sequence[float],
        weighted_statistics: Sequence[float],
        total_weighted_load: float,
    ) -> float:
        """
        Evaluate a complete A-Z integer-position-indexed layout.

        Every letter must contain a valid position index, and every
        indexed position must already have a key-position cost.
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

        total_cost = 0.0

        for letter_index, weighted_count in enumerate(
            weighted_statistics
        ):
            if weighted_count == 0.0:
                continue

            total_cost += (
                weighted_count
                * position_costs[
                    positions[letter_index]
                ]
            )

        return (
            total_cost
            / total_weighted_load
        )

    def _indexed_weighted_statistics(
        self,
        statistics: CharacterStatistics,
    ) -> tuple[float, ...]:
        cache_key = id(
            statistics
        )

        cached = (
            self._weighted_statistics_cache.get(
                cache_key
            )
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
                counts[index] += weighted_count

        result = tuple(
            counts
        )

        self._weighted_statistics_cache[
            cache_key
        ] = result

        return result
