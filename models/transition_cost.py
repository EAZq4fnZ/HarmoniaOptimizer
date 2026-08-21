# models/transition_cost.py

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class TransitionCostWeights:
    """
    Weights used to calculate transition cost.

    Lower total cost is better.

    Penalties increase cost.
    Rewards decrease cost.
    """

    same_finger_penalty: float
    same_hand_penalty: float
    row_change_penalty: float

    alternation_reward: float
    inward_roll_reward: float
    outward_roll_reward: float


@dataclass(slots=True, frozen=True)
class TransitionCost:
    """
    Numeric cost breakdown for a single transition.

    Lower total cost is better.
    """

    same_finger: float
    same_hand: float
    row_change: float
    alternation: float
    roll: float

    @property
    def total(self) -> float:
        return (
            self.same_finger
            + self.same_hand
            + self.row_change
            + self.alternation
            + self.roll
        )