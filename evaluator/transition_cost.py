# evaluator/transition_cost.py

from models.enums import RollDirection
from models.transition_cost import (
    TransitionCost,
    TransitionCostWeights,
)
from models.transition_evaluation import TransitionEvaluation


class TransitionCostEvaluator:
    """
    Convert a TransitionEvaluation into numeric cost.

    Lower cost is better.

    The evaluator contains no fixed ergonomic weights.
    All weights are supplied externally.
    """

    def __init__(
        self,
        weights: TransitionCostWeights,
    ) -> None:
        self._weights = weights

    def evaluate(
        self,
        evaluation: TransitionEvaluation,
    ) -> TransitionCost:
        same_finger_cost = (
            self._weights.same_finger_penalty
            if evaluation.is_same_finger
            else 0.0
        )

        same_hand_cost = (
            self._weights.same_hand_penalty
            if evaluation.is_same_hand
            else 0.0
        )

        row_change_cost = (
            0.0
            if evaluation.is_same_row
            else self._weights.row_change_penalty
        )

        alternation_cost = (
            -self._weights.alternation_reward
            if evaluation.is_alternating
            else 0.0
        )

        roll_cost = self._roll_cost(
            evaluation.roll_direction
        )

        return TransitionCost(
            same_finger=same_finger_cost,
            same_hand=same_hand_cost,
            row_change=row_change_cost,
            alternation=alternation_cost,
            roll=roll_cost,
        )

    def _roll_cost(
        self,
        direction: RollDirection,
    ) -> float:
        if direction is RollDirection.INWARD:
            return -self._weights.inward_roll_reward

        if direction is RollDirection.OUTWARD:
            return -self._weights.outward_roll_reward

        return 0.0