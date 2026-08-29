# optimizer/vowel_seed_builder.py

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping
from itertools import combinations, permutations
from math import comb, perm
from typing import cast

from evaluator.candidate_evaluator import CandidateEvaluator
from evaluator.character_statistics import CharacterStatistics
from evaluator.fast_candidate_evaluator import (
    FastCandidateEvaluator,
)
from evaluator.transition_statistics import TransitionStatistics
from models.candidate_evaluation import CandidateEvaluation
from models.layout import Layout


class VowelSeedBuilder:
    """
    Build the best valid vowel seed for a set of allowed positions.

    All assignments of A/E/I/O/U to five distinct allowed positions
    are evaluated.

    Optional left-hand vowel limits can be supplied. When they are
    supplied, only assignments satisfying the requested hand
    distribution are generated.

    An optional fast evaluator can be supplied for exhaustive search.

    When the fast evaluator is present, candidate layouts are represented
    as A-Z indexed position lists during exhaustive search. This avoids
    constructing a Layout or a complete letter-to-position mapping for
    every candidate.

    Only the final winning indexed candidate is converted back into a
    mapping and Layout and evaluated with the normal CandidateEvaluator.

    An optional progress callback can also be supplied by the caller.
    """

    VOWELS = ("A", "E", "I", "O", "U")

    VOWEL_INDEXES = (
        0,   # A
        4,   # E
        8,   # I
        14,  # O
        20,  # U
    )

    LETTER_COUNT = 26
    A_ORD = ord("A")

    def __init__(
        self,
        evaluator: CandidateEvaluator,
        allowed_positions: frozenset[str],
        fast_evaluator: FastCandidateEvaluator | None = None,
    ) -> None:
        if len(allowed_positions) < len(self.VOWELS):
            raise ValueError(
                "allowed_positions must contain at least 5 positions"
            )

        self._evaluator = evaluator
        self._fast_evaluator = fast_evaluator
        self._allowed_positions = allowed_positions
        self._evaluated_candidate_count = 0

    @property
    def allowed_positions(self) -> frozenset[str]:
        return self._allowed_positions

    @property
    def evaluated_candidate_count(self) -> int:
        return self._evaluated_candidate_count

    def build(
        self,
        layout: Layout,
        transition_statistics: TransitionStatistics,
        character_statistics: CharacterStatistics,
        progress_callback: (
            Callable[[int, int], None] | None
        ) = None,
        progress_interval: int = 1000,
        min_left_vowels: int | None = None,
        max_left_vowels: int | None = None,
    ) -> CandidateEvaluation:
        """
        Search vowel assignments and return the best valid one.

        Normal path:
            Layout objects are evaluated normally.

        Fast path:
            Logical positions are converted to integer IDs once.
            Exhaustive search then operates on 26-entry integer
            position lists.

            Only the final winning candidate is converted back
            into a Layout.
        """

        if progress_interval <= 0:
            raise ValueError(
                "progress_interval must be greater than 0"
            )

        self._validate_hand_limits(
            min_left_vowels=min_left_vowels,
            max_left_vowels=max_left_vowels,
        )

        candidate_positions = tuple(
            sorted(self._allowed_positions)
        )

        left_positions = tuple(
            position
            for position in candidate_positions
            if position.startswith("L-")
        )

        right_positions = tuple(
            position
            for position in candidate_positions
            if position.startswith("R-")
        )

        self._evaluated_candidate_count = 0

        total_candidates = self._count_candidate_positions(
            candidate_positions=candidate_positions,
            min_left_vowels=min_left_vowels,
            max_left_vowels=max_left_vowels,
        )

        best: CandidateEvaluation | None = None

        best_score: float | None = None
        best_position_indexes: list[int] | None = None

        position_indexes: dict[str, int] | None = None

        cost_matrix: (
            tuple[
                tuple[float, ...],
                ...
            ]
            | None
        ) = None

        position_finger_indexes: (
            tuple[int, ...]
            | None
        ) = None

        allowed_ratios: (
            tuple[float, ...]
            | None
        ) = None

        base_position_indexes: (
            list[int]
            | None
        ) = None

        original_vowel_position_indexes: (
            frozenset[int]
            | None
        ) = None

        original_vowel_position_indexes_sorted: (
            tuple[int, ...]
            | None
        ) = None

        letter_index_by_position_index: (
            tuple[int, ...]
            | None
        ) = None

        position_ids_by_index: (
            tuple[str, ...]
            | None
        ) = None

        prepared_finger_load_baseline = None

        prepared_transitions = None

        prepared_weighted_statistics: (
            tuple[float, ...]
            | None
        ) = None

        prepared_total_weighted_load: (
            float
            | None
        ) = None

        candidate_position_indexes: tuple[int, ...] | None = None
        left_position_indexes: tuple[int, ...] | None = None
        right_position_indexes: tuple[int, ...] | None = None

        if self._fast_evaluator is not None:
            base_string_positions = (
                self._layout_to_indexed_positions(
                    layout
                )
            )

            # Important:
            # position integer IDs are assigned in lexicographic
            # logical-position order.
            #
            # This means sorting integer position IDs preserves
            # the exact behavior of:
            #
            #     sorted(vacated_positions)
            #
            # in the original string-based implementation.
            position_ids_by_index = tuple(
                sorted(
                    position
                    for position
                    in base_string_positions
                    if position is not None
                )
            )

            (
                position_indexes,
                cost_matrix,
                position_finger_indexes,
                allowed_ratios,
            ) = (
                self
                ._fast_evaluator
                .prepare_position_index(
                    position_ids_by_index
                )
            )

            base_position_indexes = [
                (
                    -1
                    if position is None
                    else position_indexes[
                        position
                    ]
                )
                for position
                in base_string_positions
            ]

            original_vowel_position_indexes = (
                frozenset(
                    base_position_indexes[
                        vowel_index
                    ]
                    for vowel_index
                    in self.VOWEL_INDEXES
                )
            )

            original_vowel_position_indexes_sorted = tuple(
                sorted(
                    original_vowel_position_indexes
                )
            )

            mutable_letter_indexes = [
                -1
            ] * len(
                position_ids_by_index
            )

            for (
                letter_index,
                position_index,
            ) in enumerate(
                base_position_indexes
            ):
                if position_index >= 0:
                    mutable_letter_indexes[
                        position_index
                    ] = letter_index

            if any(
                letter_index < 0
                for letter_index
                in mutable_letter_indexes
            ):
                raise RuntimeError(
                    "incomplete position-to-letter index"
                )

            letter_index_by_position_index = (
                tuple(
                    mutable_letter_indexes
                )
            )

            prepared_transitions = (
                self
                ._fast_evaluator
                .prepare_position_indexed_transitions(
                    transition_statistics
                )
            )

            (
                prepared_weighted_statistics,
                prepared_total_weighted_load,
            ) = (
                self
                ._fast_evaluator
                .prepare_position_indexed_character_statistics(
                    character_statistics
                )
            )

            # Finger-load baseline is prepared per selected vowel
            # position set inside the exhaustive loop. Consonant positions
            # are fixed for all 5! permutations in that group.
            prepared_finger_load_baseline = None

            candidate_position_indexes = tuple(
                position_indexes[position]
                for position in candidate_positions
            )
            left_position_indexes = tuple(
                position_indexes[position]
                for position in left_positions
            )
            right_position_indexes = tuple(
                position_indexes[position]
                for position in right_positions
            )

        vowel_position_source: Iterator[
            tuple[
                tuple[str, ...] | tuple[int, ...],
                tuple[int, ...] | None,
                tuple[int, ...] | None,
                tuple[int, ...] | None,
            ]
        ]

        if self._fast_evaluator is None:
            vowel_position_source = (
                (
                    vowel_positions,
                    None,
                    None,
                    None,
                )
                for vowel_positions
                in self._generate_vowel_positions(
                    candidate_positions=candidate_positions,
                    left_positions=left_positions,
                    right_positions=right_positions,
                    min_left_vowels=min_left_vowels,
                    max_left_vowels=max_left_vowels,
                )
            )
        else:
            if (
                candidate_position_indexes is None
                or left_position_indexes is None
                or right_position_indexes is None
                or original_vowel_position_indexes is None
                or original_vowel_position_indexes_sorted is None
                or letter_index_by_position_index is None
            ):
                raise RuntimeError(
                    "integer vowel-position data "
                    "was not initialized"
                )

            vowel_position_source = (
                self._generate_grouped_vowel_position_indexes(
                    candidate_position_indexes=(
                        candidate_position_indexes
                    ),
                    left_position_indexes=(
                        left_position_indexes
                    ),
                    right_position_indexes=(
                        right_position_indexes
                    ),
                    min_left_vowels=min_left_vowels,
                    max_left_vowels=max_left_vowels,
                    original_vowel_positions=(
                        original_vowel_position_indexes
                    ),
                    original_vowel_positions_sorted=(
                        original_vowel_position_indexes_sorted
                    ),
                    letter_index_by_position=(
                        letter_index_by_position_index
                    ),
                )
            )

        consonant_transition_cost: float | None = None

        for (
            vowel_positions,
            displaced_letter_indexes,
            vacated_positions,
            selected_positions,
        ) in vowel_position_source:
            self._evaluated_candidate_count += 1

            if self._fast_evaluator is None:
                string_vowel_positions = tuple(
                    str(position)
                    for position in vowel_positions
                )

                candidate_layout = self._assign_vowels(
                    layout=layout,
                    vowel_positions=string_vowel_positions,
                )

                evaluation = self._evaluator.evaluate(
                    layout=candidate_layout,
                    transition_statistics=transition_statistics,
                    character_statistics=character_statistics,
                )

                if (
                    evaluation.is_valid
                    and evaluation.score is not None
                    and (
                        best is None
                        or (
                            best.score is not None
                            and evaluation.score < best.score
                        )
                    )
                ):
                    best = evaluation

            else:
                if (
                    position_indexes is None
                    or cost_matrix is None
                    or position_finger_indexes is None
                    or allowed_ratios is None
                    or base_position_indexes is None
                    or original_vowel_position_indexes is None
                    or original_vowel_position_indexes_sorted is None
                    or letter_index_by_position_index is None
                    or prepared_transitions is None
                    or prepared_weighted_statistics is None
                    or prepared_total_weighted_load is None
                ):
                    raise RuntimeError(
                        "position-indexed search data "
                        "was not initialized"
                    )

                integer_vowel_positions = cast(
                    tuple[int, ...],
                    vowel_positions,
                )

                if (
                    displaced_letter_indexes is None
                    or vacated_positions is None
                    or selected_positions is None
                ):
                    raise RuntimeError(
                        "grouped vowel displacement data "
                        "was not initialized"
                    )

                (
                    candidate_position_indexes,
                    changed_letter_indexes,
                ) = (
                    self
                    ._assign_vowels_position_indexed_prepared_fast(
                        base_positions=(
                            base_position_indexes
                        ),
                        vowel_position_indexes=(
                            integer_vowel_positions
                        ),
                        displaced_letter_indexes=(
                            displaced_letter_indexes
                        ),
                        vacated_positions=(
                            vacated_positions
                        ),
                    )
                )

                if integer_vowel_positions == selected_positions:
                    consonant_transition_cost = (
                        self._fast_evaluator
                        .prepare_position_indexed_complete_consonant_cost(
                            candidate_position_indexes,
                            cost_matrix,
                            prepared_transitions,
                        )
                    )
                    prepared_finger_load_baseline = (
                        self._fast_evaluator
                        .prepare_position_indexed_complete_vowel_group_finger_load_baseline(
                            candidate_position_indexes,
                            position_finger_indexes,
                            prepared_weighted_statistics,
                            prepared_total_weighted_load,
                        )
                    )

                if consonant_transition_cost is None:
                    raise RuntimeError(
                        "consonant transition cost was not initialized"
                    )

                if prepared_finger_load_baseline is None:
                    raise RuntimeError(
                        "vowel-group finger-load baseline "
                        "was not initialized"
                    )

                score = (
                    self
                    ._fast_evaluator
                    .evaluate_fully_prepared_position_indexed_complete_finger_delta_with_consonant_cost(
                        baseline_positions=(
                            base_position_indexes
                        ),
                        positions=(
                            candidate_position_indexes
                        ),
                        cost_matrix=cost_matrix,
                        prepared_transitions=(
                            prepared_transitions
                        ),
                        consonant_cost=(
                            consonant_transition_cost
                        ),
                        position_finger_indexes=(
                            position_finger_indexes
                        ),
                        allowed_ratios=(
                            allowed_ratios
                        ),
                        weighted_statistics=(
                            prepared_weighted_statistics
                        ),
                        finger_load_baseline=(
                            prepared_finger_load_baseline
                        ),
                        changed_letter_indexes=(
                            changed_letter_indexes
                        ),
                    )
                )

                if (
                    best_score is None
                    or score < best_score
                ):
                    best_score = score
                    best_position_indexes = (
                        candidate_position_indexes
                    )

            if (
                progress_callback is not None
                and (
                    self._evaluated_candidate_count
                    % progress_interval
                    == 0
                    or self._evaluated_candidate_count
                    == total_candidates
                )
            ):
                progress_callback(
                    self._evaluated_candidate_count,
                    total_candidates,
                )

        if self._fast_evaluator is not None:
            if (
                best_position_indexes is None
                or position_ids_by_index is None
            ):
                raise ValueError(
                    "no valid vowel seed could be generated"
                )

            best_mapping = (
                self
                ._position_indexed_to_mapping(
                    best_position_indexes,
                    position_ids_by_index,
                )
            )

            best_layout = Layout(
                name=layout.name,
                version=layout.version,
                layer=layout.layer,
                description=layout.description,
                mapping=best_mapping,
            )

            best = self._evaluator.evaluate(
                layout=best_layout,
                transition_statistics=transition_statistics,
                character_statistics=character_statistics,
            )

            if (
                not best.is_valid
                or best.score is None
            ):
                raise RuntimeError(
                    "fast evaluator selected a candidate "
                    "that failed normal evaluation"
                )

        if best is None:
            raise ValueError(
                "no valid vowel seed could be generated"
            )

        return best

    def _generate_vowel_positions(
        self,
        *,
        candidate_positions: tuple[str, ...],
        left_positions: tuple[str, ...],
        right_positions: tuple[str, ...],
        min_left_vowels: int | None,
        max_left_vowels: int | None,
    ) -> Iterator[tuple[str, ...]]:
        """
        Generate vowel-position assignments.

        Without hand limits, generate all permutations.

        With hand limits, directly generate only assignments
        satisfying the requested number of left-hand vowels.
        """

        if (
            min_left_vowels is None
            or max_left_vowels is None
        ):
            yield from permutations(
                candidate_positions,
                len(self.VOWELS),
            )
            return

        vowel_indexes = tuple(
            range(len(self.VOWELS))
        )

        for left_count in range(
            min_left_vowels,
            max_left_vowels + 1,
        ):
            right_count = (
                len(self.VOWELS)
                - left_count
            )

            if left_count > len(left_positions):
                continue

            if right_count > len(right_positions):
                continue

            for left_indexes in combinations(
                vowel_indexes,
                left_count,
            ):
                left_index_set = set(
                    left_indexes
                )

                right_indexes = tuple(
                    index
                    for index in vowel_indexes
                    if index not in left_index_set
                )

                for left_assignment in permutations(
                    left_positions,
                    left_count,
                ):
                    for right_assignment in permutations(
                        right_positions,
                        right_count,
                    ):
                        result: list[str | None] = (
                            [None] * len(self.VOWELS)
                        )

                        for index, position in zip(
                            left_indexes,
                            left_assignment,
                            strict=True,
                        ):
                            result[index] = position

                        for index, position in zip(
                            right_indexes,
                            right_assignment,
                            strict=True,
                        ):
                            result[index] = position

                        if any(
                            position is None
                            for position in result
                        ):
                            raise RuntimeError(
                                "incomplete vowel assignment"
                            )

                        yield tuple(
                            position
                            for position in result
                            if position is not None
                        )

    def _generate_vowel_position_indexes(
        self,
        *,
        candidate_position_indexes: tuple[int, ...],
        left_position_indexes: tuple[int, ...],
        right_position_indexes: tuple[int, ...],
        min_left_vowels: int | None,
        max_left_vowels: int | None,
    ) -> Iterator[tuple[int, ...]]:
        """
        Generate vowel assignments directly as integer position IDs.

        This is the fast-path counterpart of _generate_vowel_positions().
        It preserves the same candidate order while avoiding per-candidate
        string-to-position-index dictionary lookups.
        """

        if (
            min_left_vowels is None
            or max_left_vowels is None
        ):
            yield from permutations(
                candidate_position_indexes,
                len(self.VOWELS),
            )
            return

        vowel_indexes = tuple(
            range(len(self.VOWELS))
        )

        for left_count in range(
            min_left_vowels,
            max_left_vowels + 1,
        ):
            right_count = (
                len(self.VOWELS)
                - left_count
            )

            if left_count > len(left_position_indexes):
                continue

            if right_count > len(right_position_indexes):
                continue

            for left_indexes in combinations(
                vowel_indexes,
                left_count,
            ):
                left_index_set = set(
                    left_indexes
                )

                right_indexes = tuple(
                    index
                    for index in vowel_indexes
                    if index not in left_index_set
                )

                for left_assignment in permutations(
                    left_position_indexes,
                    left_count,
                ):
                    for right_assignment in permutations(
                        right_position_indexes,
                        right_count,
                    ):
                        result = [0, 0, 0, 0, 0]

                        for index, position in zip(
                            left_indexes,
                            left_assignment,
                            strict=True,
                        ):
                            result[index] = position

                        for index, position in zip(
                            right_indexes,
                            right_assignment,
                            strict=True,
                        ):
                            result[index] = position

                        yield (
                            result[0],
                            result[1],
                            result[2],
                            result[3],
                            result[4],
                        )

    def _generate_grouped_vowel_position_indexes(
        self,
        *,
        candidate_position_indexes: tuple[int, ...],
        left_position_indexes: tuple[int, ...],
        right_position_indexes: tuple[int, ...],
        min_left_vowels: int | None,
        max_left_vowels: int | None,
        original_vowel_positions: frozenset[int],
        original_vowel_positions_sorted: tuple[int, ...],
        letter_index_by_position: tuple[int, ...],
    ) -> Iterator[
        tuple[
            tuple[int, ...],
            tuple[int, ...],
            tuple[int, ...],
            tuple[int, ...],
        ]
    ]:
        """
        Generate fast-path vowel assignments grouped by target set.

        Displaced letters and vacated original-vowel positions depend
        only on the unordered set of five target positions. They are
        prepared once per target set and reused for every vowel
        permutation in that set.
        """

        vowel_count = len(self.VOWELS)

        if (
            min_left_vowels is None
            or max_left_vowels is None
        ):
            for selected_positions in combinations(
                candidate_position_indexes,
                vowel_count,
            ):
                (
                    displaced_letter_indexes,
                    vacated_positions,
                ) = self._prepare_vowel_displacement(
                    selected_positions=selected_positions,
                    original_vowel_positions=(
                        original_vowel_positions
                    ),
                    original_vowel_positions_sorted=(
                        original_vowel_positions_sorted
                    ),
                    letter_index_by_position=(
                        letter_index_by_position
                    ),
                )

                for vowel_positions in permutations(
                    selected_positions,
                    vowel_count,
                ):
                    yield (
                        vowel_positions,
                        displaced_letter_indexes,
                        vacated_positions,
                        selected_positions,
                    )

            return

        for left_count in range(
            min_left_vowels,
            max_left_vowels + 1,
        ):
            right_count = (
                vowel_count
                - left_count
            )

            if left_count > len(left_position_indexes):
                continue

            if right_count > len(right_position_indexes):
                continue

            for selected_left_positions in combinations(
                left_position_indexes,
                left_count,
            ):
                for selected_right_positions in combinations(
                    right_position_indexes,
                    right_count,
                ):
                    selected_positions = (
                        selected_left_positions
                        + selected_right_positions
                    )

                    (
                        displaced_letter_indexes,
                        vacated_positions,
                    ) = self._prepare_vowel_displacement(
                        selected_positions=(
                            selected_positions
                        ),
                        original_vowel_positions=(
                            original_vowel_positions
                        ),
                        original_vowel_positions_sorted=(
                            original_vowel_positions_sorted
                        ),
                        letter_index_by_position=(
                            letter_index_by_position
                        ),
                    )

                    for vowel_positions in permutations(
                        selected_positions,
                        vowel_count,
                    ):
                        yield (
                            vowel_positions,
                            displaced_letter_indexes,
                            vacated_positions,
                            selected_positions,
                        )

    def _prepare_vowel_displacement(
        self,
        *,
        selected_positions: tuple[int, ...],
        original_vowel_positions: frozenset[int],
        original_vowel_positions_sorted: tuple[int, ...],
        letter_index_by_position: tuple[int, ...],
    ) -> tuple[
        tuple[int, ...],
        tuple[int, ...],
    ]:
        """
        Prepare displacement metadata for one unordered target set.
        """

        selected_position_set = set(
            selected_positions
        )

        displaced_letter_indexes = tuple(
            sorted(
                letter_index_by_position[
                    position_index
                ]
                for position_index
                in selected_positions
                if (
                    position_index
                    not in original_vowel_positions
                )
            )
        )

        vacated_positions = tuple(
            position_index
            for position_index
            in original_vowel_positions_sorted
            if position_index not in selected_position_set
        )

        return (
            displaced_letter_indexes,
            vacated_positions,
        )

    def _count_candidate_positions(
        self,
        *,
        candidate_positions: tuple[str, ...],
        min_left_vowels: int | None,
        max_left_vowels: int | None,
    ) -> int:
        """
        Return the number of assignments that will be evaluated.

        When hand limits are active, calculate the total
        combinatorially instead of enumerating candidates.
        """

        if (
            min_left_vowels is None
            or max_left_vowels is None
        ):
            return perm(
                len(candidate_positions),
                len(self.VOWELS),
            )

        left_count_available = sum(
            position.startswith("L-")
            for position in candidate_positions
        )

        right_count_available = (
            len(candidate_positions)
            - left_count_available
        )

        total = 0

        for left_vowel_count in range(
            min_left_vowels,
            max_left_vowels + 1,
        ):
            right_vowel_count = (
                len(self.VOWELS)
                - left_vowel_count
            )

            if (
                left_vowel_count
                > left_count_available
            ):
                continue

            if (
                right_vowel_count
                > right_count_available
            ):
                continue

            total += (
                comb(
                    len(self.VOWELS),
                    left_vowel_count,
                )
                * perm(
                    left_count_available,
                    left_vowel_count,
                )
                * perm(
                    right_count_available,
                    right_vowel_count,
                )
            )

        return total

    def _validate_hand_limits(
        self,
        *,
        min_left_vowels: int | None,
        max_left_vowels: int | None,
    ) -> None:
        """
        Validate optional left-hand vowel limits.
        """

        if (
            min_left_vowels is None
            and max_left_vowels is None
        ):
            return

        if (
            min_left_vowels is None
            or max_left_vowels is None
        ):
            raise ValueError(
                "min_left_vowels and max_left_vowels "
                "must be supplied together"
            )

        if min_left_vowels < 0:
            raise ValueError(
                "min_left_vowels must be greater than "
                "or equal to 0"
            )

        if max_left_vowels > len(self.VOWELS):
            raise ValueError(
                "max_left_vowels must not exceed "
                "the number of vowels"
            )

        if min_left_vowels > max_left_vowels:
            raise ValueError(
                "min_left_vowels must not exceed "
                "max_left_vowels"
            )

    def _assign_vowels_mapping(
        self,
        layout: Layout,
        vowel_positions: tuple[str, ...],
    ) -> dict[str, str]:
        """
        Return a mapping with vowels assigned to vowel_positions.

        This preserves the exact displacement semantics of
        _assign_vowels().

        Consonants displaced from target positions are moved into
        positions vacated by the vowels.

        This mapping path remains available for compatibility and
        testing. The fast exhaustive-search path uses
        _assign_vowels_indexed() instead.
        """

        self._validate_vowel_positions(
            vowel_positions
        )

        original_vowel_positions = {
            layout.position(vowel)
            for vowel in self.VOWELS
        }

        target_positions = set(
            vowel_positions
        )

        displaced_positions = (
            target_positions
            - original_vowel_positions
        )

        vacated_positions = (
            original_vowel_positions
            - target_positions
        )

        displaced_letters = tuple(
            sorted(
                layout.letter(position)
                for position in displaced_positions
            )
        )

        available_positions = tuple(
            sorted(vacated_positions)
        )

        if len(displaced_letters) != len(
            available_positions
        ):
            raise ValueError(
                "displaced-letter and vacated-position "
                "counts differ"
            )

        mapping = dict(
            layout.items()
        )

        for vowel, position in zip(
            self.VOWELS,
            vowel_positions,
            strict=True,
        ):
            mapping[vowel] = position

        for letter, position in zip(
            displaced_letters,
            available_positions,
            strict=True,
        ):
            mapping[letter] = position

        return mapping

    def _mapping_to_indexed_positions(
        self,
        mapping: Mapping[str, str],
    ) -> list[str | None]:
        """
        Convert an A-Z mapping to a 26-entry indexed position list.

        index 0  -> A
        index 1  -> B
        ...
        index 25 -> Z

        This helper remains available for compatibility and tests.
        Fast exhaustive search does not use this conversion anymore.
        """

        positions: list[str | None] = [
            None
        ] * self.LETTER_COUNT

        for letter, position in mapping.items():
            index = self._letter_index(
                letter
            )

            if index is not None:
                positions[index] = position

        return positions

    def _layout_to_indexed_positions(
        self,
        layout: Layout,
    ) -> list[str | None]:
        """
        Convert the original layout into A-Z indexed positions.

        This is performed once before exhaustive fast search.
        """

        positions: list[str | None] = [
            None
        ] * self.LETTER_COUNT

        for letter, position in layout.items():
            index = self._letter_index(
                letter
            )

            if index is not None:
                positions[index] = position

        return positions

    def _assign_vowels_indexed(
        self,
        layout: Layout,
        base_positions: list[str | None],
        vowel_positions: tuple[str, ...],
    ) -> list[str | None]:
        """
        Return a 26-entry indexed position list with vowels assigned.

        This preserves exactly the same displacement semantics as
        _assign_vowels_mapping(), without constructing a mapping or
        Layout for every candidate.
        """

        self._validate_vowel_positions(
            vowel_positions
        )

        if len(base_positions) != self.LETTER_COUNT:
            raise ValueError(
                "base_positions must contain exactly 26 entries"
            )

        original_vowel_positions = {
            layout.position(vowel)
            for vowel in self.VOWELS
        }

        target_positions = set(
            vowel_positions
        )

        displaced_positions = (
            target_positions
            - original_vowel_positions
        )

        vacated_positions = (
            original_vowel_positions
            - target_positions
        )

        displaced_letters = tuple(
            sorted(
                layout.letter(position)
                for position in displaced_positions
            )
        )

        available_positions = tuple(
            sorted(vacated_positions)
        )

        if len(displaced_letters) != len(
            available_positions
        ):
            raise ValueError(
                "displaced-letter and vacated-position "
                "counts differ"
            )

        positions = list(
            base_positions
        )

        for vowel, position in zip(
            self.VOWELS,
            vowel_positions,
            strict=True,
        ):
            index = self._letter_index(
                vowel
            )

            if index is None:
                raise RuntimeError(
                    "vowel could not be converted "
                    "to an alphabet index"
                )

            positions[index] = position

        for letter, position in zip(
            displaced_letters,
            available_positions,
            strict=True,
        ):
            index = self._letter_index(
                letter
            )

            if index is None:
                raise RuntimeError(
                    "displaced letter could not be converted "
                    "to an alphabet index"
                )

            positions[index] = position

        return positions

    def _assign_vowels_position_indexed(
        self,
        *,
        base_positions: list[int],
        vowel_position_indexes: tuple[int, ...],
        original_vowel_positions: frozenset[int],
        letter_index_by_position: tuple[int, ...],
    ) -> list[int]:
        """
        Assign vowels using integer logical-position IDs only.

        This preserves the displacement semantics of
        _assign_vowels_mapping() and _assign_vowels_indexed().

        The exhaustive-search hot path avoids constructing
        target/displaced/vacated sets for every candidate.
        """

        if (
            len(vowel_position_indexes)
            != len(self.VOWELS)
        ):
            raise ValueError(
                "vowel_position_indexes must contain "
                "exactly 5 positions"
            )

        if (
            len(set(vowel_position_indexes))
            != len(self.VOWELS)
        ):
            raise ValueError(
                "vowel_position_indexes must be unique"
            )

        (
            target_0,
            target_1,
            target_2,
            target_3,
            target_4,
        ) = vowel_position_indexes

        displaced_positions: list[int] = []

        if target_0 not in original_vowel_positions:
            displaced_positions.append(
                target_0
            )

        if target_1 not in original_vowel_positions:
            displaced_positions.append(
                target_1
            )

        if target_2 not in original_vowel_positions:
            displaced_positions.append(
                target_2
            )

        if target_3 not in original_vowel_positions:
            displaced_positions.append(
                target_3
            )

        if target_4 not in original_vowel_positions:
            displaced_positions.append(
                target_4
            )

        vacated_positions = [
            position_index
            for position_index
            in original_vowel_positions
            if (
                position_index != target_0
                and position_index != target_1
                and position_index != target_2
                and position_index != target_3
                and position_index != target_4
            )
        ]

        displaced_letter_indexes = [
            letter_index_by_position[
                position_index
            ]
            for position_index
            in displaced_positions
        ]

        displaced_letter_indexes.sort()
        vacated_positions.sort()

        if (
            len(displaced_letter_indexes)
            != len(vacated_positions)
        ):
            raise ValueError(
                "displaced-letter and vacated-position "
                "counts differ"
            )

        positions = list(
            base_positions
        )

        positions[
            self.VOWEL_INDEXES[0]
        ] = target_0

        positions[
            self.VOWEL_INDEXES[1]
        ] = target_1

        positions[
            self.VOWEL_INDEXES[2]
        ] = target_2

        positions[
            self.VOWEL_INDEXES[3]
        ] = target_3

        positions[
            self.VOWEL_INDEXES[4]
        ] = target_4

        for (
            letter_index,
            position_index,
        ) in zip(
            displaced_letter_indexes,
            vacated_positions,
            strict=True,
        ):
            positions[
                letter_index
            ] = position_index

        return positions

    def _assign_vowels_position_indexed_fast(
        self,
        *,
        base_positions: list[int],
        vowel_position_indexes: tuple[int, ...],
        original_vowel_positions: frozenset[int],
        original_vowel_positions_sorted: tuple[int, ...],
        letter_index_by_position: tuple[int, ...],
    ) -> tuple[list[int], tuple[int, ...]]:
        """
        Assign vowels for the exhaustive-search hot path.

        Preconditions are guaranteed by candidate generation:

        - vowel_position_indexes contains exactly five entries.
        - all five position indexes are unique.
        - the base layout is a complete A-Z layout.

        The checked _assign_vowels_position_indexed() method remains
        available for compatibility and testing.
        """

        (
            target_0,
            target_1,
            target_2,
            target_3,
            target_4,
        ) = vowel_position_indexes

        displaced_letter_indexes: list[int] = []

        if target_0 not in original_vowel_positions:
            displaced_letter_indexes.append(
                letter_index_by_position[target_0]
            )

        if target_1 not in original_vowel_positions:
            displaced_letter_indexes.append(
                letter_index_by_position[target_1]
            )

        if target_2 not in original_vowel_positions:
            displaced_letter_indexes.append(
                letter_index_by_position[target_2]
            )

        if target_3 not in original_vowel_positions:
            displaced_letter_indexes.append(
                letter_index_by_position[target_3]
            )

        if target_4 not in original_vowel_positions:
            displaced_letter_indexes.append(
                letter_index_by_position[target_4]
            )

        # original_vowel_positions_sorted is already sorted once
        # before exhaustive search, so no per-candidate sort is needed.
        vacated_positions = [
            position_index
            for position_index
            in original_vowel_positions_sorted
            if (
                position_index != target_0
                and position_index != target_1
                and position_index != target_2
                and position_index != target_3
                and position_index != target_4
            )
        ]

        # Preserve the exact displacement semantics of the normal path:
        # displaced letters are assigned in alphabetical/index order.
        displaced_letter_indexes.sort()

        positions = base_positions.copy()

        positions[0] = target_0
        positions[4] = target_1
        positions[8] = target_2
        positions[14] = target_3
        positions[20] = target_4

        for (
            letter_index,
            position_index,
        ) in zip(
            displaced_letter_indexes,
            vacated_positions,
            strict=True,
        ):
            positions[
                letter_index
            ] = position_index

        changed_letter_indexes = (
            0,
            4,
            8,
            14,
            20,
            *displaced_letter_indexes,
        )

        return (
            positions,
            changed_letter_indexes,
        )

    def _assign_vowels_position_indexed_prepared_fast(
        self,
        *,
        base_positions: list[int],
        vowel_position_indexes: tuple[int, ...],
        displaced_letter_indexes: tuple[int, ...],
        vacated_positions: tuple[int, ...],
    ) -> tuple[list[int], tuple[int, ...]]:
        """
        Assign vowels using displacement metadata prepared per target set.
        """

        (
            target_0,
            target_1,
            target_2,
            target_3,
            target_4,
        ) = vowel_position_indexes

        positions = base_positions.copy()

        positions[0] = target_0
        positions[4] = target_1
        positions[8] = target_2
        positions[14] = target_3
        positions[20] = target_4

        for (
            letter_index,
            position_index,
        ) in zip(
            displaced_letter_indexes,
            vacated_positions,
            strict=True,
        ):
            positions[
                letter_index
            ] = position_index

        changed_letter_indexes = (
            0,
            4,
            8,
            14,
            20,
            *displaced_letter_indexes,
        )

        return (
            positions,
            changed_letter_indexes,
        )

    def _position_indexed_to_mapping(
        self,
        positions: list[int],
        position_ids_by_index: tuple[str, ...],
    ) -> dict[str, str]:
        """
        Convert A-Z indexed integer logical positions back
        into the normal letter-to-position mapping.

        This is used only for the final winning candidate.
        """

        if len(positions) != self.LETTER_COUNT:
            raise ValueError(
                "positions must contain exactly 26 entries"
            )

        mapping: dict[str, str] = {}

        for (
            letter_index,
            position_index,
        ) in enumerate(
            positions
        ):
            if position_index < 0:
                continue

            letter = chr(
                self.A_ORD
                + letter_index
            )

            mapping[letter] = (
                position_ids_by_index[
                    position_index
                ]
            )

        return mapping

    def _indexed_positions_to_mapping(
        self,
        positions: list[str | None],
    ) -> dict[str, str]:
        """
        Convert indexed A-Z positions back into a mapping.

        This is used only for the final winning candidate.
        """

        if len(positions) != self.LETTER_COUNT:
            raise ValueError(
                "positions must contain exactly 26 entries"
            )

        mapping: dict[str, str] = {}

        for index, position in enumerate(
            positions
        ):
            if position is None:
                continue

            letter = chr(
                self.A_ORD
                + index
            )

            mapping[letter] = position

        return mapping

    def _validate_vowel_positions(
        self,
        vowel_positions: tuple[str, ...],
    ) -> None:
        """
        Validate a five-position vowel assignment.
        """

        if len(vowel_positions) != len(self.VOWELS):
            raise ValueError(
                "vowel_positions must contain exactly 5 positions"
            )

        if len(set(vowel_positions)) != len(self.VOWELS):
            raise ValueError(
                "vowel_positions must be unique"
            )

    def _letter_index(
        self,
        letter: str,
    ) -> int | None:
        """
        Return A-Z index for a single ASCII letter.

        A -> 0
        ...
        Z -> 25

        Return None for unsupported IDs.
        """

        if len(letter) != 1:
            return None

        index = (
            ord(letter.upper())
            - self.A_ORD
        )

        if (
            0
            <= index
            < self.LETTER_COUNT
        ):
            return index

        return None

    def _assign_vowels(
        self,
        layout: Layout,
        vowel_positions: tuple[str, ...],
    ) -> Layout:
        """
        Return a new Layout with vowels assigned to vowel_positions.

        This is the object-producing compatibility version of
        _assign_vowels_mapping().
        """

        mapping = self._assign_vowels_mapping(
            layout=layout,
            vowel_positions=vowel_positions,
        )

        return Layout(
            name=layout.name,
            version=layout.version,
            layer=layout.layer,
            description=layout.description,
            mapping=mapping,
        )
