# models/trigram_features.py

from __future__ import annotations

from dataclasses import dataclass

from .enums import RollDirection
from .logical_key import LogicalKey


@dataclass(slots=True, frozen=True)
class TrigramFeatures:
    """
    Structural ergonomic features of a three-key sequence.

    same_finger_skip
        The first and third keys use the same hand and finger,
        while neither adjacent pair is a same-finger bigram.

        This is the broad structural SFS category.

    same_hand_same_finger_skip
        A same-finger skip where all three keys are on the
        same hand.

    alternating_same_finger_skip
        A same-finger skip where the middle key is on the
        opposite hand. This is therefore also an alternating
        L-R-L or R-L-R trigram.

    alternating_hands
        The hand sequence is L-R-L or R-L-R.

    same_hand
        All three keys are on the same hand.

    roll_direction
        INWARD or OUTWARD when both adjacent movements are
        valid rolls in the same direction.

    redirect
        True when both adjacent movements are valid rolls but
        their directions are opposite.
    """

    first: LogicalKey
    second: LogicalKey
    third: LogicalKey

    same_finger_skip: bool
    same_hand_same_finger_skip: bool
    alternating_same_finger_skip: bool

    alternating_hands: bool
    same_hand: bool

    roll_direction: RollDirection
    redirect: bool
