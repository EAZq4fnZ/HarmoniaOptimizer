# optimizer/swap_candidate_generator.py

from __future__ import annotations

from itertools import combinations

from models.layout import Layout
from models.swap_candidate import SwapCandidate
from models.swap_move import SwapMove
from optimizer.layout_mutator import LayoutMutator


class SwapCandidateGenerator:
    """
    Generate candidate layouts by swapping every pair of letters.

    For a 26-letter alphabet this produces:

        C(26, 2) = 325 candidates
    """

    def __init__(
        self,
        mutator: LayoutMutator | None = None,
    ) -> None:
        self._mutator = mutator or LayoutMutator()

    def generate(
        self,
        layout: Layout,
    ) -> tuple[Layout, ...]:
        """
        Generate every unique one-swap layout.

        The original layout itself is not included.

        This method is preserved for backward compatibility.
        """

        return tuple(
            candidate.layout
            for candidate in self.generate_candidates(layout)
        )

    def generate_candidates(
        self,
        layout: Layout,
    ) -> tuple[SwapCandidate, ...]:
        """
        Generate every unique one-swap candidate.

        Each candidate preserves both:

        - the swap operation
        - the resulting layout
        """

        letters = tuple(sorted(layout.letters()))

        return tuple(
            self._make_candidate(
                layout,
                letter1,
                letter2,
            )
            for letter1, letter2 in combinations(
                letters,
                2,
            )
        )

    def _make_candidate(
        self,
        layout: Layout,
        first_letter: str,
        second_letter: str,
    ) -> SwapCandidate:
        move = SwapMove(
            first_letter=first_letter,
            second_letter=second_letter,
        )

        candidate_layout = self._mutator.swap(
            layout,
            first_letter,
            second_letter,
        )

        return SwapCandidate(
            move=move,
            layout=candidate_layout,
        )