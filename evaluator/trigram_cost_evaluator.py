# evaluator/trigram_cost_evaluator.py

from __future__ import annotations

from models.enums import RollDirection
from models.trigram_cost import TrigramCost, TrigramCostWeights
from models.trigram_features import TrigramFeatures


class TrigramCostEvaluator:
    """
    Convert trigram ergonomic features into a numeric cost.

    Lower is better.

    Cost precedence
    ---------------
    A same-finger skip may also structurally be a redirect.
    In that case the same-finger-skip penalty takes precedence
    and the redirect penalty is not applied.

    Feature classification itself remains unchanged.
    """

    def __init__(
        self,
        weights: TrigramCostWeights,
    ) -> None:
        self._weights = weights

    @property
    def weights(self) -> TrigramCostWeights:
        return self._weights

    def evaluate(
        self,
        features: TrigramFeatures,
    ) -> TrigramCost:
        same_finger_skip = 0.0
        redirect = 0.0
        alternation = 0.0
        inward_roll = 0.0
        outward_roll = 0.0

        if features.same_finger_skip:
            same_finger_skip = (
                self._weights.same_finger_skip_penalty
            )
        elif features.redirect:
            redirect = self._weights.redirect_penalty

        if features.alternating_hands:
            alternation = -self._weights.alternation_reward

        if features.roll_direction is RollDirection.INWARD:
            inward_roll = -self._weights.inward_roll_reward
        elif features.roll_direction is RollDirection.OUTWARD:
            outward_roll = -self._weights.outward_roll_reward

        return TrigramCost(
            same_finger_skip=same_finger_skip,
            redirect=redirect,
            alternation=alternation,
            inward_roll=inward_roll,
            outward_roll=outward_roll,
        )
