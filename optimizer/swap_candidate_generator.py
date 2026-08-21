# optimizer/swap_candidate_generator.py

from __future__ import annotations

from itertools import combinations

from models.layout import Layout
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
        Generate every unique one-swap candidate.

        The original layout itself is not included.
        """

        letters = tuple(sorted(layout.letters()))

        candidates = tuple(
            self._mutator.swap(
                layout,
                letter1,
                letter2,
            )
            for letter1, letter2 in combinations(
                letters,
                2,
            )
        )

        return candidates