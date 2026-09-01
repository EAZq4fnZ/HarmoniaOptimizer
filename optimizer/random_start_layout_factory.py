# optimizer/random_start_layout_factory.py

from __future__ import annotations

from random import Random

from models.layout import Layout


class RandomStartLayoutFactory:
    """
    Create reproducible random starting layouts.

    Each run is derived independently from the
    configured seed and run index, so generation
    does not depend on call order.
    """

    def __init__(
        self,
        seed: int,
    ) -> None:
        self._seed = seed

    @property
    def seed(self) -> int:
        return self._seed

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

        letters = sorted(
            base_layout.mapping
        )

        positions = [
            base_layout.mapping[letter]
            for letter in letters
        ]

        rng = Random(
            f"{self._seed}:{run_index}"
        )

        rng.shuffle(positions)

        mapping = dict(
            zip(
                letters,
                positions,
                strict=True,
            )
        )

        return Layout(
            name=(
                f"{base_layout.name}"
                f"_random_{run_index:04d}"
            ),
            version=base_layout.version,
            layer=base_layout.layer,
            description=(
                base_layout.description
            ),
            mapping=mapping,
        )
