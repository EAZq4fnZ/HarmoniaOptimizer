# evaluator/roll_detector.py

from models.enums import Finger, Hand, RollDirection
from models.transition import Transition

_FINGER_ORDER = {
    Finger.PINKY: 0,
    Finger.RING: 1,
    Finger.MIDDLE: 2,
    Finger.INDEX: 3,
}


def detect_roll_direction(
    transition: Transition,
) -> RollDirection:
    """
    Detect roll direction for a transition.

    Rules
    -----
    - Different hands -> NONE
    - Same finger -> NONE
    - Only adjacent-finger movements are considered rolls
    - Left hand:
        pinky -> ring -> middle -> index = INWARD
        index -> middle -> ring -> pinky = OUTWARD
    - Right hand:
        index -> middle -> ring -> pinky = INWARD
        pinky -> ring -> middle -> index = OUTWARD
    """

    source = transition.source.position
    target = transition.target.position

    if source.hand != target.hand:
        return RollDirection.NONE

    if source.finger == target.finger:
        return RollDirection.NONE

    source_index = _FINGER_ORDER[source.finger]
    target_index = _FINGER_ORDER[target.finger]

    difference = target_index - source_index

    if abs(difference) != 1:
        return RollDirection.NONE

    if source.hand is Hand.LEFT:
        if difference == 1:
            return RollDirection.INWARD

        return RollDirection.OUTWARD

    if source.hand is Hand.RIGHT:
        if difference == -1:
            return RollDirection.INWARD

        return RollDirection.OUTWARD

    return RollDirection.NONE