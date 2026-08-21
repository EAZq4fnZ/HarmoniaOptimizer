# evaluator/constraint_set.py

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from models.constraint_evaluation import ConstraintEvaluation
from models.layout import Layout


class LayoutConstraint(Protocol):
    """
    Protocol implemented by constraints that evaluate a Layout.
    """

    def evaluate(
        self,
        layout: Layout,
    ) -> ConstraintEvaluation:
        ...


class ConstraintSet:
    """
    Evaluate multiple layout constraints as one constraint set.
    """

    def __init__(
        self,
        constraints: Iterable[LayoutConstraint],
    ) -> None:
        self._constraints = tuple(constraints)

    @property
    def constraints(
        self,
    ) -> tuple[LayoutConstraint, ...]:
        return self._constraints

    def evaluate(
        self,
        layout: Layout,
    ) -> ConstraintEvaluation:
        violations = []

        for constraint in self._constraints:
            evaluation = constraint.evaluate(layout)
            violations.extend(evaluation.violations)

        return ConstraintEvaluation(
            violations=tuple(violations)
        )