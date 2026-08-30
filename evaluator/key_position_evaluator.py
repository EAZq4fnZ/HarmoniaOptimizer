from __future__ import annotations

from evaluator.character_statistics import CharacterStatistics
from models.key_position_cost import KeyPositionCostProfile
from models.key_position_evaluation import KeyPositionEvaluation
from models.layout import Layout


class KeyPositionEvaluator:
    """
    Evaluate unigram character frequency against key-position costs.

    Lower score is better.
    """

    def __init__(
        self,
        profile: KeyPositionCostProfile,
    ) -> None:
        self._profile = profile

    @property
    def profile(self) -> KeyPositionCostProfile:
        return self._profile

    def evaluate(
        self,
        layout: Layout,
        statistics: CharacterStatistics,
    ) -> KeyPositionEvaluation:
        total_cost = 0.0
        evaluated_weight = 0.0
        skipped_weight = 0.0

        for character, weighted_count in (
            statistics.weighted().items()
        ):
            character_id = character.upper()

            position_id = layout.mapping.get(
                character_id
            )

            if position_id is None:
                skipped_weight += weighted_count
                continue

            position_cost = self._profile.cost(
                position_id
            )

            if position_cost is None:
                skipped_weight += weighted_count
                continue

            total_cost += (
                position_cost
                * weighted_count
            )
            evaluated_weight += weighted_count

        return KeyPositionEvaluation(
            total_cost=total_cost,
            evaluated_weight=evaluated_weight,
            skipped_weight=skipped_weight,
        )
