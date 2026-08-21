# evaluator/finger_load_budget_evaluator.py

from __future__ import annotations

from models.finger_load import FingerLoad
from models.finger_load_budget import FingerLoadBudget
from models.finger_load_evaluation import FingerLoadEvaluation


class FingerLoadBudgetEvaluator:
    """
    Compare actual finger loads with target load budgets.
    """

    def evaluate(
        self,
        loads: tuple[FingerLoad, ...],
        budgets: tuple[FingerLoadBudget, ...],
    ) -> tuple[FingerLoadEvaluation, ...]:
        """
        Evaluate weighted finger-load ratios.

        Penalty is applied only when actual load exceeds
        target_ratio + tolerance.
        """

        total_weighted_load = sum(
            load.weighted_count
            for load in loads
        )

        load_map = {
            (load.hand, load.finger): load
            for load in loads
        }

        results: list[FingerLoadEvaluation] = []

        for budget in budgets:
            load = load_map.get(
                (budget.hand, budget.finger)
            )

            weighted_count = (
                load.weighted_count
                if load is not None
                else 0.0
            )

            if total_weighted_load > 0.0:
                actual_ratio = (
                    weighted_count / total_weighted_load
                )
            else:
                actual_ratio = 0.0

            allowed_ratio = (
                budget.target_ratio
                + budget.tolerance
            )

            excess_ratio = max(
                0.0,
                actual_ratio - allowed_ratio,
            )

            results.append(
                FingerLoadEvaluation(
                    hand=budget.hand,
                    finger=budget.finger,
                    actual_ratio=actual_ratio,
                    target_ratio=budget.target_ratio,
                    tolerance=budget.tolerance,
                    excess_ratio=excess_ratio,
                    penalty=excess_ratio,
                )
            )

        return tuple(results)