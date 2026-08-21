# evaluator/transition_evaluator.py

from models.transition import Transition
from models.transition_evaluation import TransitionEvaluation

from .transition_features import extract_transition_features


class TransitionEvaluator:
    """
    Evaluate structural properties of a key transition.

    This evaluator does not assign numeric costs.
    """

    def evaluate(
        self,
        transition: Transition,
    ) -> TransitionEvaluation:
        features = extract_transition_features(transition)

        return TransitionEvaluation(
            transition=transition,
            features=features,
            is_alternating=features.alternating_hands,
            is_same_hand=features.same_hand,
            is_same_finger=features.same_finger,
            is_same_row=features.same_row,
            roll_direction=features.roll_direction,
        )