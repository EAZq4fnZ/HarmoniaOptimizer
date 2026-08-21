# evaluator/finger_load_pipeline.py

from __future__ import annotations

from evaluator.character_statistics import CharacterStatistics
from evaluator.finger_load_budget_evaluator import (
    FingerLoadBudgetEvaluator,
)
from evaluator.finger_load_evaluator import FingerLoadEvaluator
from models.finger_load_budget import FingerLoadBudget
from models.finger_load_evaluation import FingerLoadEvaluation
from models.layout import Layout


class FingerLoadPipeline:
    """
    Evaluate finger load for a complete layout.

    Pipeline
    --------
    CharacterStatistics
        -> FingerLoadEvaluator
        -> FingerLoad
        -> FingerLoadBudgetEvaluator
        -> FingerLoadEvaluation
    """

    def __init__(self) -> None:
        self._load_evaluator = FingerLoadEvaluator()
        self._budget_evaluator = FingerLoadBudgetEvaluator()

    def evaluate(
        self,
        layout: Layout,
        statistics: CharacterStatistics,
        budgets: tuple[FingerLoadBudget, ...],
    ) -> tuple[FingerLoadEvaluation, ...]:
        """
        Evaluate finger-load penalties for a layout.
        """

        loads = self._load_evaluator.evaluate(
            layout,
            statistics,
        )

        return self._budget_evaluator.evaluate(
            loads,
            budgets,
        )