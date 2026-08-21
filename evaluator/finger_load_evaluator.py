# evaluator/finger_load_evaluator.py

from __future__ import annotations

from collections import defaultdict

from models.enums import Finger, Hand
from models.finger_load import FingerLoad
from models.layout import Layout
from models.layout_key_mapper import LayoutKeyMapper

from .character_statistics import CharacterStatistics


class FingerLoadEvaluator:
    """
    Calculate character load for every hand/finger pair.
    """

    def evaluate(
        self,
        layout: Layout,
        statistics: CharacterStatistics,
    ) -> tuple[FingerLoad, ...]:
        """
        Evaluate finger load for a layout.

        Characters that are not present in the layout are ignored.
        """

        mapper = LayoutKeyMapper(layout)

        raw_loads: dict[tuple[Hand, Finger], int] = defaultdict(int)
        weighted_loads: dict[tuple[Hand, Finger], float] = defaultdict(float)

        for character, raw_count in statistics.raw().items():
            try:
                key = mapper.key(character)
            except KeyError:
                continue

            pair = (
                key.position.hand,
                key.position.finger,
            )

            raw_loads[pair] += raw_count

        for character, weighted_count in statistics.weighted().items():
            try:
                key = mapper.key(character)
            except KeyError:
                continue

            pair = (
                key.position.hand,
                key.position.finger,
            )

            weighted_loads[pair] += weighted_count

        pairs = set(raw_loads) | set(weighted_loads)

        return tuple(
            FingerLoad(
                hand=hand,
                finger=finger,
                raw_count=raw_loads[(hand, finger)],
                weighted_count=weighted_loads[(hand, finger)],
            )
            for hand, finger in sorted(
                pairs,
                key=lambda pair: (
                    pair[0].value,
                    pair[1].value,
                ),
            )
        )