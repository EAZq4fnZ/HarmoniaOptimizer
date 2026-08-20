# evaluator/transition_features.py

from models.transition import Transition
from models.transition_features import TransitionFeatures


def extract_transition_features(
    transition: Transition,
) -> TransitionFeatures:
    """
    Extract structural features from a transition.
    """

    source = transition.source.position
    target = transition.target.position

    same_hand = source.hand == target.hand
    same_finger = (
        same_hand
        and source.finger == target.finger
    )

    return TransitionFeatures(
        transition=transition,
        same_hand=same_hand,
        same_finger=same_finger,
        same_row=source.row == target.row,
        alternating_hands=not same_hand,
    )