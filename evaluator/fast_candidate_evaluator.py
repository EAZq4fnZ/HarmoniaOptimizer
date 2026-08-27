# evaluator/fast_candidate_evaluator.py

from __future__ import annotations

from collections.abc import Mapping, Sequence

from evaluator.character_statistics import CharacterStatistics
from evaluator.constraint_set import ConstraintSet
from evaluator.fast_candidate_scorer import FastCandidateScorer
from evaluator.fast_finger_load_score_evaluator import (
    FastFingerLoadScoreEvaluator,
)
from evaluator.fast_layout_score_evaluator import (
    FastLayoutScoreEvaluator,
    PositionIndexedDeltaBaseline,
    PreparedPositionIndexedDeltaBaseline,
    PreparedPositionIndexedTransitions,
)
from evaluator.transition_statistics import TransitionStatistics
from models.layout import Layout



class FastCandidateEvaluator:
    """
    Evaluate one candidate layout for exhaustive search.

    Returns only the final numeric score.

    Invalid candidates return None.

    Unlike CandidateEvaluator, this evaluator does not construct
    detailed layout, transition, finger-load, or candidate-score
    result objects.

    Several fast paths are provided:

        evaluate()
            Layout-based compatibility path.

        evaluate_mapping()
            Mapping-based exhaustive-search path.

        evaluate_indexed()
            A-Z indexed path using string logical-position IDs.

        evaluate_position_indexed()
            Fully position-indexed path.

        evaluate_position_indexed_delta()
            Fully position-indexed path using delta transition
            evaluation from a prepared baseline.
    """

    def __init__(
        self,
        constraint_set: ConstraintSet,
        layout_evaluator: FastLayoutScoreEvaluator,
        finger_load_evaluator: FastFingerLoadScoreEvaluator,
        candidate_scorer: FastCandidateScorer,
    ) -> None:
        self._constraint_set = constraint_set
        self._layout_evaluator = layout_evaluator
        self._finger_load_evaluator = finger_load_evaluator
        self._candidate_scorer = candidate_scorer

    def evaluate(
        self,
        layout: Layout,
        transition_statistics: TransitionStatistics,
        character_statistics: CharacterStatistics,
    ) -> float | None:
        """
        Return the final candidate score.

        Invalid candidates are rejected before the more expensive
        scoring stages are evaluated.
        """

        constraint_evaluation = (
            self._constraint_set.evaluate(
                layout
            )
        )

        if not constraint_evaluation.is_valid:
            return None

        return self._score_mapping(
            mapping=layout.mapping,
            transition_statistics=transition_statistics,
            character_statistics=character_statistics,
        )

    def evaluate_mapping(
        self,
        mapping: Mapping[str, str],
        transition_statistics: TransitionStatistics,
        character_statistics: CharacterStatistics,
    ) -> float:
        """
        Return the final score for an already validated mapping.

        This method intentionally skips ConstraintSet evaluation.

        It is intended for exhaustive-search paths where candidate
        generation itself guarantees that all required constraints
        are satisfied.

        Unlike evaluate(), no Layout object is required.
        """

        return self._score_mapping(
            mapping=mapping,
            transition_statistics=transition_statistics,
            character_statistics=character_statistics,
        )

    def evaluate_indexed(
        self,
        positions: list[str | None],
        transition_statistics: TransitionStatistics,
        character_statistics: CharacterStatistics,
    ) -> float:
        """
        Return the final score using indexed evaluation paths.

        Both transition cost and finger-load scoring use
        A-Z indexed positions.
        """

        layout_score = (
            self._layout_evaluator.evaluate_indexed(
                positions,
                transition_statistics,
            )
        )

        finger_load_penalty = (
            self._finger_load_evaluator.evaluate_indexed(
                positions,
                character_statistics,
            )
        )

        return self._candidate_scorer.score(
            transition_total_cost=layout_score.total_cost,
            evaluated_transition_weight=(
                layout_score.evaluated_weight
            ),
            finger_load_penalty=finger_load_penalty,
        )

    def evaluate_position_indexed(
        self,
        positions: list[int],
        cost_matrix: tuple[
            tuple[float, ...],
            ...,
        ],
        position_finger_indexes: tuple[int, ...],
        allowed_ratios: tuple[float, ...],
        transition_statistics: TransitionStatistics,
        character_statistics: CharacterStatistics,
    ) -> float:
        """
        Return the final score using fully position-indexed paths.

        positions contains A-Z indexed integer logical-position IDs.

        Transition scoring uses a precomputed position cost matrix.
        Finger-load scoring uses a precomputed position-to-finger
        lookup table.

        This path performs no logical-position string lookup inside
        either scoring hot loop.
        """

        layout_score = (
            self._layout_evaluator.evaluate_position_indexed(
                positions,
                cost_matrix,
                transition_statistics,
            )
        )

        finger_load_penalty = (
            self
            ._finger_load_evaluator
            .evaluate_position_indexed(
                positions,
                position_finger_indexes,
                allowed_ratios,
                character_statistics,
            )
        )

        return self._candidate_scorer.score(
            transition_total_cost=layout_score.total_cost,
            evaluated_transition_weight=(
                layout_score.evaluated_weight
            ),
            finger_load_penalty=finger_load_penalty,
        )

    def evaluate_position_indexed_flat(
        self,
        positions: list[int],
        flat_costs: tuple[float, ...],
        position_count: int,
        position_finger_indexes: tuple[int, ...],
        allowed_ratios: tuple[float, ...],
        transition_statistics: TransitionStatistics,
        character_statistics: CharacterStatistics,
    ) -> float:
        """
        Return the final score using fully position-indexed paths
        with a flat transition-cost table.

        positions contains A-Z indexed integer logical-position IDs.

        Transition scoring uses a precomputed flat row-major
        position cost table.

        Finger-load scoring uses the existing precomputed
        position-to-finger lookup table.
        """

        layout_score = (
            self._layout_evaluator
            .evaluate_position_indexed_flat(
                positions,
                flat_costs,
                position_count,
                transition_statistics,
            )
        )

        finger_load_penalty = (
            self._finger_load_evaluator
            .evaluate_position_indexed(
                positions,
                position_finger_indexes,
                allowed_ratios,
                character_statistics,
            )
        )

        return self._candidate_scorer.score(
            transition_total_cost=layout_score.total_cost,
            evaluated_transition_weight=(
                layout_score.evaluated_weight
            ),
            finger_load_penalty=finger_load_penalty,
        )

    def prepare_position_index(
        self,
        positions: Sequence[str],
    ) -> tuple[
        dict[str, int],
        tuple[
            tuple[float, ...],
            ...,
        ],
        tuple[int, ...],
        tuple[float, ...],
    ]:
        """
        Prepare all lookup tables required by the fully
        position-indexed exhaustive-search path.

        This method is intended to be called once before search.

        Returns:

            position_indexes
                Logical-position string -> integer position ID.

            cost_matrix
                Transition cost matrix indexed by integer
                position IDs.

            position_finger_indexes
                Integer position ID -> compact finger-load slot.

            allowed_ratios
                Maximum allowed load ratio for each finger slot.
        """

        (
            position_indexes,
            cost_matrix,
        ) = (
            self
            ._layout_evaluator
            .build_position_index(
                positions
            )
        )

        (
            position_finger_indexes,
            allowed_ratios,
        ) = (
            self
            ._finger_load_evaluator
            .build_position_finger_index(
                positions,
                position_indexes,
            )
        )

        return (
            position_indexes,
            cost_matrix,
            position_finger_indexes,
            allowed_ratios,
        )

    def prepare_flat_position_index(
        self,
        positions: Sequence[str],
    ) -> tuple[
        dict[str, int],
        tuple[float, ...],
        int,
        tuple[int, ...],
        tuple[float, ...],
    ]:
        """
        Prepare all lookup tables required by the flat
        position-indexed exhaustive-search path.

        Returns:

            position_indexes
                Logical-position string -> integer position ID.

            flat_costs
                Flat row-major transition-cost table.

            position_count
                Number of indexed logical positions.

            position_finger_indexes
                Integer position ID -> compact finger-load slot.

            allowed_ratios
                Maximum allowed load ratio for each finger slot.
        """

        (
            position_indexes,
            flat_costs,
            position_count,
        ) = (
            self._layout_evaluator
            .build_flat_position_costs(
                positions
            )
        )

        (
            position_finger_indexes,
            allowed_ratios,
        ) = (
            self._finger_load_evaluator
            .build_position_finger_index(
                positions,
                position_indexes,
            )
        )

        return (
            position_indexes,
            flat_costs,
            position_count,
            position_finger_indexes,
            allowed_ratios,
        )

    def prepare_transition_delta_baseline(
        self,
        positions: Sequence[int],
        cost_matrix: Sequence[
            Sequence[float]
        ],
        transition_statistics: TransitionStatistics,
    ) -> PositionIndexedDeltaBaseline:
        """
        Prepare baseline transition data for delta evaluation.

        This performs one complete position-indexed transition
        evaluation and stores the per-transition weighted
        contributions required by later delta evaluations.

        It is intended to be called once before exhaustive search.
        """

        return (
            self
            ._layout_evaluator
            .prepare_position_indexed_delta(
                positions,
                cost_matrix,
                transition_statistics,
            )
        )

    def evaluate_position_indexed_delta(
        self,
        positions: list[int],
        cost_matrix: tuple[
            tuple[float, ...],
            ...,
        ],
        position_finger_indexes: tuple[int, ...],
        allowed_ratios: tuple[float, ...],
        transition_statistics: TransitionStatistics,
        character_statistics: CharacterStatistics,
        transition_baseline: PositionIndexedDeltaBaseline,
        changed_letter_indexes: Sequence[int],
    ) -> float:
        """
        Return the final score using delta transition evaluation.

        Transition scoring:
            Reuse the prepared baseline and recalculate only
            transitions involving changed letters.

        Finger-load scoring:
            Perform the normal fully position-indexed finger-load
            evaluation.

        This method assumes candidate generation has already
        guaranteed all required hard constraints.
        """

        layout_score = (
            self
            ._layout_evaluator
            .evaluate_position_indexed_delta(
                positions,
                cost_matrix,
                transition_statistics,
                transition_baseline,
                changed_letter_indexes,
            )
        )

        finger_load_penalty = (
            self
            ._finger_load_evaluator
            .evaluate_position_indexed(
                positions,
                position_finger_indexes,
                allowed_ratios,
                character_statistics,
            )
        )

        return self._candidate_scorer.score(
            transition_total_cost=layout_score.total_cost,
            evaluated_transition_weight=(
                layout_score.evaluated_weight
            ),
            finger_load_penalty=finger_load_penalty,
        )

    def _score_mapping(
        self,
        *,
        mapping: Mapping[str, str],
        transition_statistics: TransitionStatistics,
        character_statistics: CharacterStatistics,
    ) -> float:
        """
        Score a mapping without constructing a Layout.
        """

        layout_score = (
            self._layout_evaluator.evaluate_mapping(
                mapping,
                transition_statistics,
            )
        )

        finger_load_penalty = (
            self._finger_load_evaluator.evaluate_mapping(
                mapping,
                character_statistics,
            )
        )

        return self._candidate_scorer.score(
            transition_total_cost=layout_score.total_cost,
            evaluated_transition_weight=(
                layout_score.evaluated_weight
            ),
            finger_load_penalty=finger_load_penalty,
        )

    def prepare_position_indexed_transitions(
        self,
        transition_statistics: TransitionStatistics,
    ) -> PreparedPositionIndexedTransitions:
        return (
            self._layout_evaluator
            .prepare_position_indexed_transitions(
                transition_statistics
            )
        )

    def prepare_prepared_position_indexed_delta(
        self,
        positions: Sequence[int],
        cost_matrix: Sequence[
            Sequence[float]
        ],
        prepared_transitions: (
            PreparedPositionIndexedTransitions
        ),
    ) -> PreparedPositionIndexedDeltaBaseline:
        """
        Prepare the baseline used by prepared delta evaluation.

        This is intended to be called once before exhaustive search.
        """

        return (
            self
            ._layout_evaluator
            .prepare_prepared_position_indexed_delta(
                positions,
                cost_matrix,
                prepared_transitions,
            )
        )

    def evaluate_prepared_position_indexed(
        self,
        positions: list[int],
        cost_matrix: tuple[
            tuple[float, ...],
            ...
        ],
        prepared_transitions: PreparedPositionIndexedTransitions,
        position_finger_indexes: tuple[int, ...],
        allowed_ratios: tuple[float, ...],
        character_statistics: CharacterStatistics,
    ) -> float:
        layout_score = (
            self._layout_evaluator
            .evaluate_prepared_position_indexed(
                positions,
                cost_matrix,
                prepared_transitions,
            )
        )

        finger_load_penalty = (
            self._finger_load_evaluator
            .evaluate_position_indexed(
                positions,
                position_finger_indexes,
                allowed_ratios,
                character_statistics,
            )
        )

        return self._candidate_scorer.score(
            transition_total_cost=layout_score.total_cost,
            evaluated_transition_weight=(
                layout_score.evaluated_weight
            ),
            finger_load_penalty=finger_load_penalty,
        )

    def evaluate_prepared_position_indexed_complete(
        self,
        positions: list[int],
        cost_matrix: tuple[
            tuple[float, ...],
            ...
        ],
        prepared_transitions: PreparedPositionIndexedTransitions,
        position_finger_indexes: tuple[int, ...],
        allowed_ratios: tuple[float, ...],
        character_statistics: CharacterStatistics,
    ) -> float:
        """
        Return the final score for a complete A-Z position-indexed layout.

        This uses the specialized prepared transition hot path that assumes
        every letter has a valid position index.
        """

        layout_score = (
            self._layout_evaluator
            .evaluate_prepared_position_indexed_complete(
                positions,
                cost_matrix,
                prepared_transitions,
            )
        )

        finger_load_penalty = (
            self._finger_load_evaluator
            .evaluate_position_indexed(
                positions,
                position_finger_indexes,
                allowed_ratios,
                character_statistics,
            )
        )

        return self._candidate_scorer.score(
            transition_total_cost=layout_score.total_cost,
            evaluated_transition_weight=(
                layout_score.evaluated_weight
            ),
            finger_load_penalty=finger_load_penalty,
        )

    def evaluate_prepared_position_indexed_complete_flat(
        self,
        positions: list[int],
        flat_costs: tuple[float, ...],
        position_count: int,
        prepared_transitions: PreparedPositionIndexedTransitions,
        position_finger_indexes: tuple[int, ...],
        allowed_ratios: tuple[float, ...],
        character_statistics: CharacterStatistics,
    ) -> float:
        """
        Return the final score for a complete A-Z position-indexed layout
        using a flat transition-cost table.

        This uses the specialized prepared transition hot path that assumes
        every letter has a valid position index.

        Transition scoring uses a flat row-major position-cost table.
        Finger-load scoring continues to use the normal fully
        position-indexed path.
        """

        layout_score = (
            self._layout_evaluator
            .evaluate_prepared_position_indexed_complete_flat(
                positions,
                flat_costs,
                position_count,
                prepared_transitions,
            )
        )

        finger_load_penalty = (
            self._finger_load_evaluator
            .evaluate_position_indexed(
                positions,
                position_finger_indexes,
                allowed_ratios,
                character_statistics,
            )
        )

        return self._candidate_scorer.score(
            transition_total_cost=layout_score.total_cost,
            evaluated_transition_weight=(
                layout_score.evaluated_weight
            ),
            finger_load_penalty=finger_load_penalty,
        )

    def evaluate_prepared_position_indexed_delta(
        self,
        positions: list[int],
        cost_matrix: tuple[
            tuple[float, ...],
            ...,
        ],
        transition_baseline: (
            PreparedPositionIndexedDeltaBaseline
        ),
        changed_letter_indexes: Sequence[int],
        position_finger_indexes: tuple[int, ...],
        allowed_ratios: tuple[float, ...],
        character_statistics: CharacterStatistics,
    ) -> float:
        """
        Return the final score using prepared delta transition evaluation.

        Transition scoring recalculates only transitions involving
        changed letters.

        Finger-load scoring continues to use the normal fully
        position-indexed path.
        """

        layout_score = (
            self
            ._layout_evaluator
            .evaluate_prepared_position_indexed_delta(
                positions,
                cost_matrix,
                transition_baseline,
                changed_letter_indexes,
            )
        )

        finger_load_penalty = (
            self
            ._finger_load_evaluator
            .evaluate_position_indexed(
                positions,
                position_finger_indexes,
                allowed_ratios,
                character_statistics,
            )
        )

        return self._candidate_scorer.score(
            transition_total_cost=(
                layout_score.total_cost
            ),
            evaluated_transition_weight=(
                layout_score.evaluated_weight
            ),
            finger_load_penalty=(
                finger_load_penalty
            ),
        )