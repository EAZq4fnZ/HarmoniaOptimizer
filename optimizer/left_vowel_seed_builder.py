# optimizer/left_vowel_seed_builder.py

from __future__ import annotations

from itertools import permutations

from evaluator.candidate_evaluator import CandidateEvaluator
from evaluator.character_statistics import CharacterStatistics
from evaluator.transition_statistics import TransitionStatistics
from models.candidate_evaluation import CandidateEvaluation
from models.layout import Layout
from optimizer.layout_mutator import LayoutMutator


class LeftVowelSeedBuilder:
    """
    Build the best valid seed for a left-side vowel constraint.

    The builder keeps vowels A/E/I/O/U on the allowed left-side
    positions and evaluates all assignments using the existing
    CandidateEvaluator.
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

    def build(
        self,
        layout: Layout,
        transition_statistics: TransitionStatistics,
        character_statistics: CharacterStatistics,
    ) -> CandidateEvaluation:
        candidate_positions = tuple(
            sorted(self._allowed_positions)
        )

        best: CandidateEvaluation | None = None

        for vowel_positions in permutations(
            candidate_positions,
            len(self.VOWELS),
        ):
            candidate_layout = self._assign_vowels(
                layout=layout,
                vowel_positions=vowel_positions,
            )

            evaluation = self._evaluator.evaluate(
                layout=candidate_layout,
                transition_statistics=transition_statistics,
                character_statistics=character_statistics,
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
                "no valid left-vowel seed could be generated"
            )

        return best

    def _assign_vowels(
        self,
        layout: Layout,
        vowel_positions: tuple[str, ...],
    ) -> Layout:
        result = layout

        for vowel, target_position in zip(
            self.VOWELS,
            vowel_positions,
            strict=True,
        ):
            current_position = result.position(vowel)

            if current_position == target_position:
                continue

            occupant = result.letter_at(
                target_position
            )

            result = LayoutMutator.swap(
                result,
                vowel,
                occupant,
            )

        return result