# models/layout_evaluation.py

from dataclasses import dataclass

from .transition_cost import TransitionCost


@dataclass(slots=True, frozen=True)
class LayoutTransitionEvaluation:
    """
    Cost contribution of one character transition.
    """

    source: str
    target: str

    raw_count: int
    weighted_count: float

    cost: TransitionCost
    weighted_cost: float


@dataclass(slots=True, frozen=True)
class LayoutEvaluation:
    """
    Evaluation result for an entire keyboard layout.

    Lower total_cost is better.
    """

    total_cost: float

    evaluated_weight: float
    skipped_weight: float

    transitions: tuple[LayoutTransitionEvaluation, ...]

    @property
    def transition_count(self) -> int:
        return len(self.transitions)