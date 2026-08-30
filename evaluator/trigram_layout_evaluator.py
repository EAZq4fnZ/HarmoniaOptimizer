# evaluator/trigram_layout_evaluator.py

from __future__ import annotations

from models.layout import Layout
from models.layout_key_mapper import LayoutKeyMapper
from models.trigram_cost import TrigramCost, TrigramCostWeights
from models.trigram_features import TrigramFeatures
from models.trigram_layout_evaluation import (
    TrigramLayoutEvaluation,
    TrigramLayoutRecord,
)

from .trigram_cost_evaluator import TrigramCostEvaluator
from .trigram_evaluator import TrigramEvaluator
from .trigram_statistics import TrigramStatistics


class TrigramLayoutEvaluator:
    """
    Evaluate a complete layout using trigram statistics.

    Lower score is better.

    Trigram features and costs are cached by canonical logical-position
    IDs. Structural trigram properties depend on the three positions,
    not on the letters assigned to those positions.
    """

    def __init__(
        self,
        weights: TrigramCostWeights,
    ) -> None:
        self._trigram_evaluator = TrigramEvaluator()

        self._cost_evaluator = TrigramCostEvaluator(
            weights
        )

        self._trigram_cache: dict[
            tuple[str, str, str],
            tuple[TrigramFeatures, TrigramCost],
        ] = {}

    def evaluate(
        self,
        layout: Layout,
        statistics: TrigramStatistics,
    ) -> TrigramLayoutEvaluation:
        """
        Evaluate one layout against trigram statistics.
        """

        mapper = LayoutKeyMapper(
            layout
        )

        position_map = {
            letter.upper(): position
            for letter, position in layout.items()
        }

        trigram_results: list[
            TrigramLayoutRecord
        ] = []

        total_cost = 0.0
        evaluated_weight = 0.0
        skipped_weight = 0.0

        for (
            first_id,
            second_id,
            third_id,
            raw_count,
            weighted_count,
        ) in statistics.evaluation_records():
            first_position_id = position_map.get(
                first_id
            )
            second_position_id = position_map.get(
                second_id
            )
            third_position_id = position_map.get(
                third_id
            )

            if (
                first_position_id is None
                or second_position_id is None
                or third_position_id is None
            ):
                skipped_weight += weighted_count
                continue

            cache_key = (
                first_position_id,
                second_position_id,
                third_position_id,
            )

            cached = self._trigram_cache.get(
                cache_key
            )

            if cached is None:
                first_key = mapper.key(
                    first_id
                )
                second_key = mapper.key(
                    second_id
                )
                third_key = mapper.key(
                    third_id
                )

                features = self._trigram_evaluator.evaluate(
                    first_key,
                    second_key,
                    third_key,
                )

                cost = self._cost_evaluator.evaluate(
                    features
                )

                self._trigram_cache[
                    cache_key
                ] = (
                    features,
                    cost,
                )
            else:
                features, cost = cached

            weighted_cost = (
                cost.total
                * weighted_count
            )

            trigram_results.append(
                TrigramLayoutRecord(
                    first=first_id,
                    second=second_id,
                    third=third_id,
                    raw_count=raw_count,
                    weighted_count=weighted_count,
                    features=features,
                    cost=cost,
                    weighted_cost=weighted_cost,
                )
            )

            total_cost += weighted_cost
            evaluated_weight += weighted_count

        return TrigramLayoutEvaluation(
            total_cost=total_cost,
            evaluated_weight=evaluated_weight,
            skipped_weight=skipped_weight,
            trigrams=tuple(
                trigram_results
            ),
        )
