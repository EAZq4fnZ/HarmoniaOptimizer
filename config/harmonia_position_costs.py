from __future__ import annotations

from models.key_position_cost import KeyPositionCostProfile

# Harmonia v5.1b physical L0 alphabet positions.
#
# Position cost measures reach / positional difficulty.
# Finger strength and total finger usage are intentionally left to
# FingerLoad evaluation to avoid double-counting.
#
# Lower is better.
#
# Base costs:
#   normal HOME   = 0.00
#   normal TOP    = 0.20
#   normal BOTTOM = 0.25
#
# Extra index inner-column reach:
#   HOME   +0.10
#   TOP    +0.10
#   BOTTOM +0.10


HARMONIA_POSITION_COSTS: dict[str, float] = {
    # ------------------------------------------------------------
    # Left hand
    # ------------------------------------------------------------

    # Pinky
    "L-P-H-0": 0.00,

    # Ring
    "L-R-T-1": 0.20,
    "L-R-H-1": 0.00,
    "L-R-B-1": 0.25,

    # Middle
    "L-M-T-2": 0.20,
    "L-M-H-2": 0.00,
    "L-M-B-2": 0.25,

    # Index — primary column
    "L-I-T-3": 0.20,
    "L-I-H-3": 0.00,
    "L-I-B-3": 0.25,

    # Index — inner/reach column
    "L-I-T-4": 0.30,
    "L-I-H-4": 0.10,
    "L-I-B-4": 0.35,

    # ------------------------------------------------------------
    # Right hand
    # ------------------------------------------------------------

    # Pinky
    "R-P-H-0": 0.00,

    # Ring
    "R-R-T-1": 0.20,
    "R-R-H-1": 0.00,
    "R-R-B-1": 0.25,

    # Middle
    "R-M-T-2": 0.20,
    "R-M-H-2": 0.00,
    "R-M-B-2": 0.25,

    # Index — primary column
    "R-I-T-3": 0.20,
    "R-I-H-3": 0.00,
    "R-I-B-3": 0.25,

    # Index — inner/reach column
    "R-I-T-4": 0.30,
    "R-I-H-4": 0.10,
    "R-I-B-4": 0.35,
}


def make_harmonia_position_cost_profile() -> KeyPositionCostProfile:
    """
    Build the default Harmonia v5.1b key-position cost profile.

    The profile describes positional/reach difficulty only.
    Finger capacity is evaluated separately by FingerLoad.
    """

    return KeyPositionCostProfile(
        costs=HARMONIA_POSITION_COSTS
    )
