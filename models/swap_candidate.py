# models/swap_candidate.py

from __future__ import annotations

from dataclasses import dataclass

from models.layout import Layout
from models.swap_move import SwapMove


@dataclass(frozen=True, slots=True)
class SwapCandidate:
    """
    Candidate layout produced by one swap operation.
    """

    move: SwapMove
    layout: Layout