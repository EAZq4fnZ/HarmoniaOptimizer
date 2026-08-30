# evaluator/trigram_evaluator.py

from __future__ import annotations

from models.enums import RollDirection
from models.logical_key import LogicalKey
from models.transition import Transition
from models.trigram_features import TrigramFeatures

from .roll_detector import detect_roll_direction


class TrigramEvaluator:
    """
    Evaluate structural ergonomic features of a three-key sequence.

    This evaluator classifies trigrams but does not assign numeric costs.
    """

    def evaluate(
        self,
        first: LogicalKey,
        second: LogicalKey,
        third: LogicalKey,
    ) -> TrigramFeatures:
        first_position = first.position
        second_position = second.position
        third_position = third.position

        same_hand = (
            first_position.hand
            == second_position.hand
            == third_position.hand
        )

        alternating_hands = (
            first_position.hand == third_position.hand
            and first_position.hand != second_position.hand
        )

        first_second_same_finger = (
            first_position.hand == second_position.hand
            and first_position.finger == second_position.finger
        )

        second_third_same_finger = (
            second_position.hand == third_position.hand
            and second_position.finger == third_position.finger
        )

        same_finger_skip = (
            first_position.hand == third_position.hand
            and first_position.finger == third_position.finger
            and not first_second_same_finger
            and not second_third_same_finger
        )

        first_transition = Transition(
            source=first,
            target=second,
        )

        second_transition = Transition(
            source=second,
            target=third,
        )

        first_roll = detect_roll_direction(
            first_transition
        )

        second_roll = detect_roll_direction(
            second_transition
        )

        roll_direction = RollDirection.NONE
        redirect = False

        if (
            same_hand
            and first_roll is not RollDirection.NONE
            and second_roll is not RollDirection.NONE
        ):
            if first_roll is second_roll:
                roll_direction = first_roll
            else:
                redirect = True

        return TrigramFeatures(
            first=first,
            second=second,
            third=third,
            same_finger_skip=same_finger_skip,
            alternating_hands=alternating_hands,
            same_hand=same_hand,
            roll_direction=roll_direction,
            redirect=redirect,
        )
