# models/transition_features.py

from dataclasses import dataclass

from models.transition import Transition


@dataclass(slots=True, frozen=True)
class TransitionFeatures:
    transition: Transition
    alternating_hands: bool
    same_hand: bool
    same_finger: bool
    different_fingers: bool
    same_row: bool
    different_rows: bool


def extract_transition_features(
    transition: Transition,
) -> TransitionFeatures:

    source = transition.source.position
    target = transition.target.position

    return TransitionFeatures(
        transition=transition,
        alternating_hands=source.hand != target.hand,
        same_hand=source.hand == target.hand,
        same_finger=source.finger == target.finger,
        different_fingers=source.finger != target.finger,
        same_row=source.row == target.row,
        different_rows=source.row != target.row,
    )