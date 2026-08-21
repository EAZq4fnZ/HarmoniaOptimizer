# evaluator/layout_evaluator.py

from models.layout import Layout
from models.layout_evaluation import (
    LayoutEvaluation,
    LayoutTransitionEvaluation,
)
from models.layout_key_mapper import LayoutKeyMapper
from models.transition import Transition
from models.transition_cost import TransitionCostWeights

from .transition_cost import TransitionCostEvaluator
from .transition_evaluator import TransitionEvaluator
from .transition_statistics import TransitionStatistics


class LayoutEvaluator:
    """
    Evaluate a complete layout using transition statistics.

    Lower total cost is better.
    """

    def __init__(
        self,
        weights: TransitionCostWeights,
    ) -> None:
        self._transition_evaluator = TransitionEvaluator()
        self._cost_evaluator = TransitionCostEvaluator(
            weights
        )

    def evaluate(
        self,
        layout: Layout,
        statistics: TransitionStatistics,
    ) -> LayoutEvaluation:
        mapper = LayoutKeyMapper(layout)

        transition_results: list[
            LayoutTransitionEvaluation
        ] = []

        total_cost = 0.0
        evaluated_weight = 0.0
        skipped_weight = 0.0

        for (
            source_letter,
            target_letter,
        ), weighted_count in statistics.weighted().items():

            if (
                source_letter not in layout
                or target_letter not in layout
            ):
                skipped_weight += weighted_count
                continue

            source_key = mapper.key(source_letter)
            target_key = mapper.key(target_letter)

            transition = Transition(
                source=source_key,
                target=target_key,
            )

            evaluation = (
                self._transition_evaluator.evaluate(
                    transition
                )
            )

            cost = self._cost_evaluator.evaluate(
                evaluation
            )

            weighted_cost = (
                cost.total * weighted_count
            )

            raw_count = statistics.raw_count(
                source_letter,
                target_letter,
            )

            transition_results.append(
                LayoutTransitionEvaluation(
                    source=source_letter.upper(),
                    target=target_letter.upper(),
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
            transitions=tuple(transition_results),
        )