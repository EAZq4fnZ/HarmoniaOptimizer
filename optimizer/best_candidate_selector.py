# optimizer/best_candidate_selector.py

from __future__ import annotations

from collections.abc import Iterable

from models.candidate_evaluation import CandidateEvaluation


class BestCandidateSelector:
    """
    Select the valid candidate with the lowest score.
    """

    def select(
        self,
        evaluations: Iterable[CandidateEvaluation],
    ) -> CandidateEvaluation | None:
        """
        Return the valid candidate with the lowest score.

        Invalid candidates and candidates without a score are ignored.

        If no selectable candidate exists, return None.

        When multiple candidates have the same score,
        the first candidate is preserved.
        """

        best: CandidateEvaluation | None = None

        for evaluation in evaluations:
            if not evaluation.is_valid:
                continue

            if evaluation.score is None:
                continue

            if best is None:
                best = evaluation
                continue

            best_score = best.score

            if best_score is None:
                best = evaluation
                continue

            if evaluation.score < best_score:
                best = evaluation

        return best