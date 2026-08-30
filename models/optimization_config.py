# models/optimization_config.py

from __future__ import annotations

from dataclasses import dataclass, field

from models.candidate_score import CandidateScoreWeights
from models.finger_load_budget import FingerLoadBudget
from models.transition_cost import TransitionCostWeights
from models.trigram_cost import TrigramCostWeights


@dataclass(frozen=True, slots=True)
class OptimizationConfig:
    """
    Complete scoring configuration for one optimization run.
    """

    version: str
    transition_cost_weights: TransitionCostWeights
    candidate_score_weights: CandidateScoreWeights
    finger_load_budgets: tuple[FingerLoadBudget, ...]
    trigram_cost_weights: TrigramCostWeights = field(
        default_factory=TrigramCostWeights
    )

    def __post_init__(self) -> None:
        if not self.version.strip():
            raise ValueError(
                "version must not be empty"
            )

        if not self.finger_load_budgets:
            raise ValueError(
                "finger_load_budgets must not be empty"
            )