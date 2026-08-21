# models/candidate_evaluation.py

# models/candidate_evaluation.py

from __future__ import annotations

from dataclasses import dataclass

from models.candidate_score import CandidateScore
from models.constraint_evaluation import ConstraintEvaluation
from models.layout import Layout
from models.layout_evaluation import LayoutEvaluation


@dataclass(frozen=True, slots=True)
class CandidateEvaluation:
    """
    Complete evaluation result for one candidate layout.

    A candidate can be rejected by hard constraints before
    layout scoring is performed.
    """

    layout: Layout
    constraint_evaluation: ConstraintEvaluation
    layout_evaluation: LayoutEvaluation | None
    candidate_score: CandidateScore | None

    @property
    def is_valid(self) -> bool:
        """
        Return whether the candidate satisfies all hard constraints.
        """

        return self.constraint_evaluation.is_valid

    @property
    def score(self) -> float | None:
        """
        Return the final combined score.

        Invalid or otherwise unscored candidates return None.
        """

        if self.candidate_score is None:
            return None

        return self.candidate_score.total