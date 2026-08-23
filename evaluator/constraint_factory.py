# evaluator/constraint_factory.py

from __future__ import annotations

from evaluator.constraint_set import ConstraintSet
from evaluator.forbidden_position_constraint import (
    ForbiddenPositionConstraint,
)
from evaluator.vowel_position_constraint import (
    VowelPositionConstraint,
)
from models.constraint_config import ConstraintConfig


class ConstraintFactory:
    """
    Build a ConstraintSet from ConstraintConfig.
    """

    @staticmethod
    def create(
        config: ConstraintConfig,
    ) -> ConstraintSet:
        constraints = []

        if config.vowel_position.enabled:
            constraints.append(
                VowelPositionConstraint(
                    allowed_positions=(
                        config
                        .vowel_position
                        .allowed_positions
                    )
                )
            )

        if config.forbidden_position.enabled:
            constraints.append(
                ForbiddenPositionConstraint(
                    forbidden_positions=(
                        config
                        .forbidden_position
                        .forbidden_positions
                    )
                )
            )

        return ConstraintSet(
            tuple(constraints)
        )