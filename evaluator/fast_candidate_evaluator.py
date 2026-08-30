# evaluator/fast_candidate_evaluator.py

from __future__ import annotations

from collections.abc import Mapping, Sequence

from evaluator.character_statistics import CharacterStatistics
from evaluator.constraint_set import ConstraintSet
from evaluator.fast_candidate_scorer import FastCandidateScorer
from evaluator.fast_finger_load_score_evaluator import (
    FastFingerLoadScoreEvaluator,
    PreparedPositionIndexedFingerLoadBaseline,
)
from evaluator.fast_layout_score_evaluator import (
    FastLayoutScoreEvaluator,
    PositionIndexedDeltaBaseline,
    PreparedPositionIndexedDeltaBaseline,
    PreparedPositionIndexedTransitions,
    PreparedVowelGroupTransitionCosts,
)
from evaluator.fast_trigram_layout_score_evaluator import (
    FastTrigramLayoutScoreEvaluator,
    PreparedPositionIndexedTrigrams,
    PreparedVowelGroupTrigramCosts,
    TrigramCostCube,
)
from evaluator.transition_statistics import TransitionStatistics
from evaluator.trigram_statistics import TrigramStatistics
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
        trigram_layout_evaluator: (
            FastTrigramLayoutScoreEvaluator | None
        ) = None,
    ) -> None:
        self._constraint_set = constraint_set
        self._layout_evaluator = layout_evaluator
        self._finger_load_evaluator = finger_load_evaluator
        self._candidate_scorer = candidate_scorer
        self._trigram_layout_evaluator = (
            trigram_layout_evaluator
        )

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

    def prepare_position_indexed_character_statistics(
        self,
        character_statistics: CharacterStatistics,
    ) -> tuple[
        tuple[float, ...],
        float,
    ]:
        """
        Prepare A-Z weighted character statistics once for the
        complete position-indexed exhaustive-search hot path.
        """

        return (
            self._finger_load_evaluator
            .prepare_position_indexed_statistics(
                character_statistics
            )
        )

    def prepare_position_indexed_finger_load_delta_baseline(
        self,
        positions: Sequence[int],
        position_finger_indexes: Sequence[int],
        allowed_ratios: Sequence[float],
        weighted_statistics: Sequence[float],
        total_weighted_load: float,
    ) -> PreparedPositionIndexedFingerLoadBaseline:
        """
        Prepare baseline finger loads once for complete-layout delta
        evaluation during exhaustive search.
        """

        return (
            self._finger_load_evaluator
            .prepare_position_indexed_complete_delta_baseline(
                positions,
                position_finger_indexes,
                allowed_ratios,
                weighted_statistics,
                total_weighted_load,
            )
        )

    def prepare_position_indexed_trigrams(
        self,
        trigram_statistics: TrigramStatistics,
    ) -> PreparedPositionIndexedTrigrams:
        if self._trigram_layout_evaluator is None:
            raise RuntimeError(
                "trigram_layout_evaluator is not configured"
            )

        return (
            self._trigram_layout_evaluator
            .prepare_position_indexed_trigrams(
                trigram_statistics
            )
        )

    def build_trigram_cost_cube(
        self,
        positions: Sequence[str],
    ) -> TrigramCostCube:
        if self._trigram_layout_evaluator is None:
            raise RuntimeError(
                "trigram_layout_evaluator is not configured"
            )

        return (
            self._trigram_layout_evaluator
            .build_cost_cube(
                positions
            )
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

    def evaluate_fully_prepared_position_indexed_complete(
        self,
        positions: list[int],
        cost_matrix: tuple[
            tuple[float, ...],
            ...,
        ],
        prepared_transitions: PreparedPositionIndexedTransitions,
        position_finger_indexes: tuple[int, ...],
        allowed_ratios: tuple[float, ...],
        weighted_statistics: tuple[float, ...],
        total_weighted_load: float,
        trigram_cost_cube: TrigramCostCube | None = None,
        prepared_trigrams: PreparedPositionIndexedTrigrams | None = None,
    ) -> float:
        """
        Return the final score for a complete A-Z position-indexed layout
        with transition, finger-load, and optional trigram scoring.

        Transition and finger-load statistics are prepared once.

        When trigram_cost_cube and prepared_trigrams are supplied,
        trigram scoring uses the prepared scalar fast path.

        This is an exhaustive-search hot path and assumes every A-Z
        position index is valid.
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
            .evaluate_prepared_position_indexed_complete(
                positions,
                position_finger_indexes,
                allowed_ratios,
                weighted_statistics,
                total_weighted_load,
            )
        )

        trigram_total_cost = 0.0
        evaluated_trigram_weight = 0.0

        if (
            trigram_cost_cube is not None
            or prepared_trigrams is not None
        ):
            if (
                trigram_cost_cube is None
                or prepared_trigrams is None
            ):
                raise ValueError(
                    "trigram_cost_cube and prepared_trigrams "
                    "must be provided together"
                )

            if self._trigram_layout_evaluator is None:
                raise RuntimeError(
                    "trigram_layout_evaluator is not configured"
                )

            trigram_total_cost = (
                self._trigram_layout_evaluator
                .evaluate_prepared_position_indexed_complete_total_cost(
                    positions,
                    trigram_cost_cube,
                    prepared_trigrams,
                )
            )

            evaluated_trigram_weight = (
                prepared_trigrams.evaluated_weight
            )

        return self._candidate_scorer.score(
            transition_total_cost=layout_score.total_cost,
            evaluated_transition_weight=(
                layout_score.evaluated_weight
            ),
            finger_load_penalty=finger_load_penalty,
            trigram_total_cost=trigram_total_cost,
            evaluated_trigram_weight=(
                evaluated_trigram_weight
            ),
        )

    def evaluate_fully_prepared_position_indexed_complete_finger_delta(
        self,
        baseline_positions: Sequence[int],
        positions: list[int],
        cost_matrix: tuple[
            tuple[float, ...],
            ...,
        ],
        prepared_transitions: PreparedPositionIndexedTransitions,
        position_finger_indexes: tuple[int, ...],
        allowed_ratios: tuple[float, ...],
        weighted_statistics: tuple[float, ...],
        finger_load_baseline: PreparedPositionIndexedFingerLoadBaseline,
        changed_letter_indexes: Sequence[int],
    ) -> float:
        """
        Return the final score for a complete A-Z position-indexed layout.

        Transition scoring uses the normal prepared complete hot path.
        Finger-load scoring applies only changed-letter deltas to a
        precomputed baseline.
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
            .evaluate_prepared_position_indexed_complete_delta(
                baseline_positions,
                positions,
                position_finger_indexes,
                allowed_ratios,
                weighted_statistics,
                finger_load_baseline,
                changed_letter_indexes,
            )
        )

        return self._candidate_scorer.score(
            transition_total_cost=layout_score.total_cost,
            evaluated_transition_weight=(
                layout_score.evaluated_weight
            ),
            finger_load_penalty=finger_load_penalty,
        )

    def prepare_position_indexed_complete_vowel_group_trigram_costs(
        self,
        positions: Sequence[int],
        trigram_cost_cube: TrigramCostCube,
        prepared_trigrams: PreparedPositionIndexedTrigrams,
    ) -> PreparedVowelGroupTrigramCosts:
        if self._trigram_layout_evaluator is None:
            raise RuntimeError(
                "trigram_layout_evaluator is not configured"
            )

        return (
            self._trigram_layout_evaluator
            .prepare_position_indexed_complete_vowel_group_costs(
                positions,
                trigram_cost_cube,
                prepared_trigrams,
            )
        )

    def prepare_position_indexed_complete_vowel_group_transition_costs(
        self,
        positions: Sequence[int],
        selected_positions: Sequence[int],
        cost_matrix: Sequence[Sequence[float]],
        prepared_transitions: PreparedPositionIndexedTransitions,
    ) -> PreparedVowelGroupTransitionCosts:
        return (
            self._layout_evaluator
            .prepare_position_indexed_complete_vowel_group_transition_costs(
                positions,
                selected_positions,
                cost_matrix,
                prepared_transitions,
            )
        )

    def prepare_position_indexed_complete_consonant_cost(
        self,
        positions: Sequence[int],
        cost_matrix: Sequence[Sequence[float]],
        prepared_transitions: PreparedPositionIndexedTransitions,
    ) -> float:
        return (
            self._layout_evaluator
            .evaluate_prepared_position_indexed_complete_consonant_cost(
                positions,
                cost_matrix,
                prepared_transitions,
            )
        )

    def prepare_position_indexed_complete_vowel_group_finger_load_baseline(
        self,
        positions: Sequence[int],
        position_finger_indexes: Sequence[int],
        weighted_statistics: Sequence[float],
        total_weighted_load: float,
    ) -> PreparedPositionIndexedFingerLoadBaseline:
        return (
            self._finger_load_evaluator
            .prepare_position_indexed_complete_vowel_group_baseline(
                positions,
                position_finger_indexes,
                weighted_statistics,
                total_weighted_load,
            )
        )

    def prepare_complete_vowel_group_scalar_hot_path(
        self,
        prepared_transitions: PreparedPositionIndexedTransitions,
        prepared_trigrams: PreparedPositionIndexedTrigrams | None = None,
    ) -> tuple[
        FastLayoutScoreEvaluator,
        FastFingerLoadScoreEvaluator,
        FastTrigramLayoutScoreEvaluator | None,
        float,
        float,
        float,
    ]:
        """
        Prepare stable dependencies for the scalar vowel-seed hot path.

        Returns the evaluator dependencies and precomputed normalization
        factors needed by the per-permutation scalar loop.
        """

        evaluated_transition_weight = (
            prepared_transitions.evaluated_weight
        )

        if evaluated_transition_weight < 0.0:
            raise ValueError(
                "evaluated_transition_weight must be non-negative"
            )

        weights = self._candidate_scorer.weights

        transition_factor = (
            0.0
            if evaluated_transition_weight == 0.0
            else (
                weights.transition_weight
                / evaluated_transition_weight
            )
        )

        trigram_factor = 0.0

        if prepared_trigrams is not None:
            if self._trigram_layout_evaluator is None:
                raise RuntimeError(
                    "trigram_layout_evaluator is not configured"
                )

            evaluated_trigram_weight = (
                prepared_trigrams.evaluated_weight
            )

            if evaluated_trigram_weight < 0.0:
                raise ValueError(
                    "evaluated_trigram_weight must be non-negative"
                )

            if evaluated_trigram_weight != 0.0:
                trigram_factor = (
                    weights.trigram_weight
                    / evaluated_trigram_weight
                )

        return (
            self._layout_evaluator,
            self._finger_load_evaluator,
            self._trigram_layout_evaluator,
            transition_factor,
            trigram_factor,
            weights.finger_load_weight,
        )

    def evaluate_fully_prepared_position_indexed_complete_vowel_group(
        self,
        positions: list[int],
        cost_matrix: tuple[tuple[float, ...], ...],
        prepared_transitions: PreparedPositionIndexedTransitions,
        transition_group_costs: PreparedVowelGroupTransitionCosts,
        position_finger_indexes: tuple[int, ...],
        allowed_ratios: tuple[float, ...],
        weighted_statistics: tuple[float, ...],
        finger_load_baseline: PreparedPositionIndexedFingerLoadBaseline,
        trigram_cost_cube: TrigramCostCube | None = None,
        trigram_group_costs: PreparedVowelGroupTrigramCosts | None = None,
        trigram_factor: float = 0.0,
    ) -> float:
        """
        Scalar-only vowel-seed hot path.

        Transition and optional trigram normalization factors can be
        prepared outside the per-permutation loop.

        When trigram_cost_cube and trigram_group_costs are supplied,
        use the vowel-group trigram preaggregation path.
        """

        transition_total_cost = (
            self._layout_evaluator
            .evaluate_prepared_position_indexed_complete_vowel_group_total_cost(
                positions,
                cost_matrix,
                prepared_transitions,
                transition_group_costs,
            )
        )

        finger_load_penalty = (
            self._finger_load_evaluator
            .evaluate_prepared_position_indexed_complete_vowel_group(
                positions,
                position_finger_indexes,
                allowed_ratios,
                weighted_statistics,
                finger_load_baseline,
            )
        )

        evaluated_transition_weight = (
            prepared_transitions.evaluated_weight
        )

        if evaluated_transition_weight == 0.0:
            transition_score = 0.0
        else:
            transition_score = (
                transition_total_cost
                / evaluated_transition_weight
            )

        weights = self._candidate_scorer.weights

        score = (
            transition_score
            * weights.transition_weight
            + finger_load_penalty
            * weights.finger_load_weight
        )

        if (
            trigram_cost_cube is not None
            or trigram_group_costs is not None
        ):
            if (
                trigram_cost_cube is None
                or trigram_group_costs is None
            ):
                raise ValueError(
                    "trigram_cost_cube and trigram_group_costs "
                    "must be provided together"
                )

            if self._trigram_layout_evaluator is None:
                raise RuntimeError(
                    "trigram_layout_evaluator is not configured"
                )

            trigram_total_cost = (
                self._trigram_layout_evaluator
                .evaluate_prepared_position_indexed_complete_vowel_group_total_cost(
                    positions,
                    trigram_cost_cube,
                    trigram_group_costs,
                )
            )

            score += (
                trigram_total_cost
                * trigram_factor
            )

        return score
    def evaluate_fully_prepared_position_indexed_complete_finger_delta_with_consonant_cost(
        self,
        baseline_positions: Sequence[int],
        positions: list[int],
        cost_matrix: tuple[tuple[float, ...], ...],
        prepared_transitions: PreparedPositionIndexedTransitions,
        consonant_cost: float,
        position_finger_indexes: tuple[int, ...],
        allowed_ratios: tuple[float, ...],
        weighted_statistics: tuple[float, ...],
        finger_load_baseline: PreparedPositionIndexedFingerLoadBaseline,
        changed_letter_indexes: Sequence[int],
    ) -> float:
        layout_score = (
            self._layout_evaluator
            .evaluate_prepared_position_indexed_complete_with_consonant_cost(
                positions,
                cost_matrix,
                prepared_transitions,
                consonant_cost,
            )
        )

        finger_load_penalty = (
            self._finger_load_evaluator
            .evaluate_prepared_position_indexed_complete_vowel_group(
                positions,
                position_finger_indexes,
                allowed_ratios,
                weighted_statistics,
                finger_load_baseline,
            )
        )

        return self._candidate_scorer.score(
            transition_total_cost=layout_score.total_cost,
            evaluated_transition_weight=layout_score.evaluated_weight,
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