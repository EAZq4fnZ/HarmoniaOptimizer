# evaluator/layout_evaluator.py

from models.layout import Layout
from models.layout_evaluation import (
    LayoutEvaluation,
    LayoutTransitionEvaluation,
)
from models.layout_key_mapper import LayoutKeyMapper
from models.transition import Transition
from models.transition_cost import (
    TransitionCost,
    TransitionCostWeights,
)

from .transition_cost import TransitionCostEvaluator
from .transition_evaluator import TransitionEvaluator
from .transition_statistics import TransitionStatistics


class LayoutEvaluator:
    """
    Evaluate a complete layout using transition statistics.

    Lower total cost is better.

    Transition costs are cached by canonical logical-position IDs.
    Structural transition cost depends on the source and target
    positions, not on the letters assigned to those positions.
    """

    def __init__(
        self,
        weights: TransitionCostWeights,
    ) -> None:
        self._transition_evaluator = (
            TransitionEvaluator()
        )

        self._cost_evaluator = (
            TransitionCostEvaluator(
                weights
            )
        )

        self._transition_cost_cache: dict[
            tuple[str, str],
            TransitionCost,
        ] = {}

    def evaluate(
        self,
        layout: Layout,
        statistics: TransitionStatistics,
    ) -> LayoutEvaluation:
        """
        Evaluate one layout against transition statistics.

        Canonical position IDs are used as the transition-cost
        cache key. LogicalKey objects are created only on cache
        misses.
        """

        mapper = LayoutKeyMapper(
            layout
        )

        position_map = {
            letter.upper(): position
            for letter, position in layout.items()
        }

        transition_results: list[
            LayoutTransitionEvaluation
        ] = []

        total_cost = 0.0
        evaluated_weight = 0.0
        skipped_weight = 0.0

        for (
            source_id,
            target_id,
            raw_count,
            weighted_count,
        ) in statistics.evaluation_records():
            source_position_id = (
                position_map.get(
                    source_id
                )
            )

            target_position_id = (
                position_map.get(
                    target_id
                )
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

            cost = (
                self
                ._transition_cost_cache
                .get(cache_key)
            )

            if cost is None:
                source_key = mapper.key(
                    source_id
                )

                target_key = mapper.key(
                    target_id
                )

                transition = Transition(
                    source=source_key,
                    target=target_key,
                )

                evaluation = (
                    self
                    ._transition_evaluator
                    .evaluate(
                        transition
                    )
                )

                cost = (
                    self
                    ._cost_evaluator
                    .evaluate(
                        evaluation
                    )
                )

                self._transition_cost_cache[
                    cache_key
                ] = cost

            weighted_cost = (
                cost.total
                * weighted_count
            )

            transition_results.append(
                LayoutTransitionEvaluation(
                    source=source_id,
                    target=target_id,
                    raw_count=raw_count,
                    weighted_count=weighted_count,
                    cost=cost,
                    weighted_cost=weighted_cost,
                )
            )

            total_cost += weighted_cost
            evaluated_weight += weighted_count

        return LayoutEvaluation(
            total_cost=total_cost,
            evaluated_weight=evaluated_weight,
            skipped_weight=skipped_weight,
            transitions=tuple(
                transition_results
            ),
        )