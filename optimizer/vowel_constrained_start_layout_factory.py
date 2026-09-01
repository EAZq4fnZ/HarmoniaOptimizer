# optimizer/vowel_constrained_start_layout_factory.py

from __future__ import annotations

from random import Random

from models.constraint_config import ConstraintConfig
from models.layout import Layout


class VowelConstrainedStartLayoutFactory:
    """
    Create reproducible random starting layouts
    that satisfy vowel-related constraints.
    """

    VOWELS = frozenset({
        "A",
        "E",
        "I",
        "O",
        "U",
    })

    def __init__(
        self,
        config: ConstraintConfig,
        seed: int,
    ) -> None:
        self._config = config
        self._seed = seed

    @property
    def seed(self) -> int:
        return self._seed

    @property
    def config(self) -> ConstraintConfig:
        return self._config

    def create(
        self,
        base_layout: Layout,
        run_index: int,
    ) -> Layout:
        if run_index < 0:
            raise ValueError(
                "run_index must be greater "
                "than or equal to 0"
            )

        rng = Random(
            f"{self._seed}:{run_index}"
        )

        positions = sorted(
            base_layout.mapping.values()
        )

        vowel_positions = (
            self._available_vowel_positions(
                positions
            )
        )

        left_positions = [
            position
            for position in vowel_positions
            if position.startswith("L-")
        ]

        right_positions = [
            position
            for position in vowel_positions
            if position.startswith("R-")
        ]

        feasible_left_counts = (
            self._feasible_left_vowel_counts(
                left_capacity=len(
                    left_positions
                ),
                right_capacity=len(
                    right_positions
                ),
            )
        )

        if not feasible_left_counts:
            raise ValueError(
                "No feasible vowel distribution "
                "for the configured constraints."
            )

        left_count = rng.choice(
            feasible_left_counts
        )

        selected_left = rng.sample(
            left_positions,
            left_count,
        )

        selected_right = rng.sample(
            right_positions,
            len(self.VOWELS) - left_count,
        )

        selected_vowel_positions = (
            selected_left
            + selected_right
        )

        vowels = sorted(self.VOWELS)

        rng.shuffle(vowels)
        rng.shuffle(
            selected_vowel_positions
        )

        mapping: dict[str, str] = {}

        for vowel, position in zip(
            vowels,
            selected_vowel_positions,
            strict=True,
        ):
            mapping[vowel] = position

        used_positions = set(
            selected_vowel_positions
        )

        remaining_positions = [
            position
            for position in positions
            if position not in used_positions
        ]

        consonants = [
            letter
            for letter in sorted(
                base_layout.mapping
            )
            if letter not in self.VOWELS
        ]

        rng.shuffle(consonants)
        rng.shuffle(
            remaining_positions
        )

        for letter, position in zip(
            consonants,
            remaining_positions,
            strict=True,
        ):
            mapping[letter] = position

        return Layout(
            name=(
                f"{base_layout.name}"
                f"_vowel_random_"
                f"{run_index:04d}"
            ),
            version=base_layout.version,
            layer=base_layout.layer,
            description=(
                base_layout.description
            ),
            mapping=mapping,
        )

    def _available_vowel_positions(
        self,
        positions: list[str],
    ) -> list[str]:
        if (
            not self
            ._config
            .vowel_position
            .enabled
        ):
            return list(positions)

        allowed_positions = (
            self
            ._config
            .vowel_position
            .allowed_positions
        )

        return [
            position
            for position in positions
            if position in allowed_positions
        ]

    def _feasible_left_vowel_counts(
        self,
        left_capacity: int,
        right_capacity: int,
    ) -> list[int]:
        vowel_count = len(self.VOWELS)

        if (
            self
            ._config
            .vowel_hand_distribution
            .enabled
        ):
            minimum = (
                self
                ._config
                .vowel_hand_distribution
                .min_left_vowels
            )

            maximum = (
                self
                ._config
                .vowel_hand_distribution
                .max_left_vowels
            )

        else:
            minimum = 0
            maximum = vowel_count

        return [
            left_count
            for left_count in range(
                minimum,
                maximum + 1,
            )
            if (
                left_count
                <= left_capacity
                and (
                    vowel_count
                    - left_count
                )
                <= right_capacity
            )
        ]
