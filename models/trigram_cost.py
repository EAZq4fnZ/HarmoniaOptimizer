# models/trigram_cost.py

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class TrigramCostWeights:
    """
    Numeric weights used to score trigram ergonomic features.

    Penalties increase the score.
    Rewards decrease the score.

    Lower total cost is better.
    """

    same_finger_skip_penalty: float = 0.0
    redirect_penalty: float = 0.0
    alternation_reward: float = 0.0
    inward_roll_reward: float = 0.0
    outward_roll_reward: float = 0.0


@dataclass(slots=True, frozen=True)
class TrigramCost:
    """
    Cost components for one trigram.

    Positive values are penalties.
    Negative values are rewards.
    """

    same_finger_skip: float = 0.0
    redirect: float = 0.0
    alternation: float = 0.0
    inward_roll: float = 0.0
    outward_roll: float = 0.0

    @property
    def total(self) -> float:
        return (
            self.same_finger_skip
            + self.redirect
            + self.alternation
            + self.inward_roll
            + self.outward_roll
        )
