# evaluator/transition_features.py

from models.transition import Transition
from models.transition_features import TransitionFeatures


def extract_transition_features(
    transition: Transition,
) -> TransitionFeatures:
    """
    Extract structural features from a transition.
    """

    source = transition.source
    target = transition.target

    return TransitionFeatures(
        transition=transition,
        same_hand=source.hand == target.hand,
        same_finger=source.finger == target.finger,
        same_row=source.row == target.row,
        alternating_hands=source.hand != target.hand,
    )
