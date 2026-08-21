# models/transition_evaluation.py

from dataclasses import dataclass

from .enums import RollDirection
from .transition import Transition
from .transition_features import TransitionFeatures


@dataclass(slots=True, frozen=True)
class TransitionEvaluation:
    """
    Evaluation result for a single transition.

    This model stores interpreted properties of a transition.
    It does not assign a numeric cost or score.
    """

    transition: Transition
    features: TransitionFeatures

    is_alternating: bool
    is_same_hand: bool
    is_same_finger: bool
    is_same_row: bool
    roll_direction: RollDirection