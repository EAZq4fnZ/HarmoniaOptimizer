# optimizer/vowel_seed_builder.py

from __future__ import annotations

from itertools import permutations

from evaluator.candidate_evaluator import CandidateEvaluator
from evaluator.character_statistics import CharacterStatistics
from evaluator.transition_statistics import TransitionStatistics
from models.candidate_evaluation import CandidateEvaluation
from models.layout import Layout


class VowelSeedBuilder:
    """
    Build the best valid vowel seed for a set of allowed positions.

    All assignments of A/E/I/O/U to five distinct allowed positions
    are evaluated. The valid candidate with the lowest score is
    returned.
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

    @property
    def allowed_positions(self) -> frozenset[str]:
        return self._allowed_positions

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
                "no valid vowel seed could be generated"
            )

        return best

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

        if len(displaced_letters) != len(available_positions):
            raise ValueError(
                "displaced-letter and vacated-position counts differ"
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