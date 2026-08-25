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

    The hand/finger pair for each logical position is cached because
    it depends only on the position, not on the letter assigned to it.
    """

    def __init__(self) -> None:
        self._position_pair_cache: dict[
            str,
            tuple[Hand, Finger],
        ] = {}

    def evaluate(
        self,
        layout: Layout,
        statistics: CharacterStatistics,
    ) -> tuple[FingerLoad, ...]:
        """
        Evaluate finger load for a layout.

        Characters that are not present in the layout are ignored.
        """

        mapper = LayoutKeyMapper(
            layout
        )

        position_map = {
            letter.upper(): position
            for letter, position in layout.items()
        }

        raw_statistics = statistics.raw()
        weighted_statistics = statistics.weighted()

        raw_loads: dict[
            tuple[Hand, Finger],
            int,
        ] = defaultdict(int)

        weighted_loads: dict[
            tuple[Hand, Finger],
            float,
        ] = defaultdict(float)

        characters = (
            set(raw_statistics)
            | set(weighted_statistics)
        )

        for character in characters:
            character_id = character.upper()

            position_id = position_map.get(
                character_id
            )

            if position_id is None:
                continue

            pair = self._position_pair_cache.get(
                position_id
            )

            if pair is None:
                key = mapper.key(
                    character_id
                )

                pair = (
                    key.position.hand,
                    key.position.finger,
                )

                self._position_pair_cache[
                    position_id
                ] = pair

            raw_count = raw_statistics.get(
                character,
                0,
            )

            weighted_count = weighted_statistics.get(
                character,
                0.0,
            )

            raw_loads[pair] += raw_count
            weighted_loads[pair] += weighted_count

        pairs = (
            set(raw_loads)
            | set(weighted_loads)
        )

        return tuple(
            FingerLoad(
                hand=hand,
                finger=finger,
                raw_count=raw_loads[
                    (hand, finger)
                ],
                weighted_count=weighted_loads[
                    (hand, finger)
                ],
            )
            for hand, finger in sorted(
                pairs,
                key=lambda pair: (
                    pair[0].value,
                    pair[1].value,
                ),
            )
        )