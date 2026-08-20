# models/transition_features.py

from dataclasses import dataclass

from .transition import Transition


@dataclass(slots=True, frozen=True)
class TransitionFeatures:
    """
    Structural characteristics of a key transition.

    This model stores facts about a transition.
    It does not assign scores or penalties.
    """

    transition: Transition
    same_hand: bool
    same_finger: bool
    same_row: bool
    alternating_hands: bool