# optimizer/vowel_seed_builder.py

from __future__ import annotations

from collections.abc import Callable, Iterator
from itertools import combinations, permutations
from math import comb, perm

from evaluator.candidate_evaluator import CandidateEvaluator
from evaluator.character_statistics import CharacterStatistics
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

    An optional progress callback can also be supplied by the caller.
    """

    VOWELS = ("A", "E", "I", "O", "U")

    def __init__(
        self,
        evaluator: CandidateEvaluator,
        allowed_positions: frozenset[str],
    ) -> None:
        if len(allowed_positions) < len(self.VOWELS):
            raise ValueError(
                "allowed_positions must contain at least 5 positions"
            )

        self._evaluator = evaluator
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

        If min_left_vowels and max_left_vowels are supplied,
        only assignments whose number of left-hand vowels falls
        within that inclusive range are generated and evaluated.

        progress_callback receives:

            completed_candidates
            total_candidates
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

        for vowel_positions in self._generate_vowel_positions(
            candidate_positions=candidate_positions,
            left_positions=left_positions,
            right_positions=right_positions,
            min_left_vowels=min_left_vowels,
            max_left_vowels=max_left_vowels,
        ):
            candidate_layout = self._assign_vowels(
                layout=layout,
                vowel_positions=vowel_positions,
            )

            self._evaluated_candidate_count += 1

            evaluation = self._evaluator.evaluate(
                layout=candidate_layout,
                transition_statistics=transition_statistics,
                character_statistics=character_statistics,
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

            if not evaluation.is_valid:
                continue

            if evaluation.score is None:
                continue

            if best is None:
                best = evaluation
                continue

            if (
                best.score is not None
                and evaluation.score < best.score
            ):
                best = evaluation

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

    def _assign_vowels(
        self,
        layout: Layout,
        vowel_positions: tuple[str, ...],
    ) -> Layout:
        """
        Return a new layout with vowels assigned to vowel_positions.

        Consonants displaced from target positions are moved into
        positions vacated by the vowels.
        """

        if len(vowel_positions) != len(self.VOWELS):
            raise ValueError(
                "vowel_positions must contain exactly 5 positions"
            )

        if len(set(vowel_positions)) != len(self.VOWELS):
            raise ValueError(
                "vowel_positions must be unique"
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

        return Layout(
            name=layout.name,
            version=layout.version,
            layer=layout.layer,
            description=layout.description,
            mapping=mapping,
        )