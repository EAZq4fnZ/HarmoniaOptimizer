# models/swap_candidate_evaluation.py

from __future__ import annotations

from dataclasses import dataclass

from models.candidate_evaluation import CandidateEvaluation
from models.swap_candidate import SwapCandidate


@dataclass(frozen=True, slots=True)
class SwapCandidateEvaluation:
    """
    Evaluation result for one swap candidate.

    Preserves both:

    - the swap operation and resulting layout
    - the candidate evaluation
    """

    candidate: SwapCandidate
    evaluation: CandidateEvaluation

    @property
    def move(self):
        """
        Return the swap move that produced the candidate.
        """

        return self.candidate.move

    @property
    def layout(self):
        """
        Return the layout produced by the swap.
        """

        return self.candidate.layout

    @property
    def is_valid(self) -> bool:
        """
        Return whether the candidate satisfies all hard constraints.
        """

        return self.evaluation.is_valid

    @property
    def score(self) -> float | None:
        """
        Return the evaluated candidate score.
        """

        return self.evaluation.score