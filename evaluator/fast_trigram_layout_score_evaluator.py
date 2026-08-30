# evaluator/fast_trigram_layout_score_evaluator.py

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from models.enums import Hand, RollDirection
from models.logical_position import LogicalPosition
from models.logical_position_parser import LogicalPositionParser
from models.trigram_cost import TrigramCostWeights

from .trigram_statistics import TrigramStatistics

_FINGER_ORDER = {
    "PINKY": 0,
    "RING": 1,
    "MIDDLE": 2,
    "INDEX": 3,
}


TrigramCostCube = tuple[
    tuple[
        tuple[float, ...],
        ...,
    ],
    ...,
]


@dataclass(frozen=True, slots=True)
class FastTrigramLayoutScore:
    """
    Minimal trigram-layout evaluation result for exhaustive search.

    Unlike TrigramLayoutEvaluation, this object does not retain
    per-trigram feature or cost details.
    """

    total_cost: float
    evaluated_weight: float
    skipped_weight: float

    @property
    def score(self) -> float:
        """
        Return normalized trigram cost.

        Lower is better.
        """

        if self.evaluated_weight == 0.0:
            return 0.0

        return self.total_cost / self.evaluated_weight


@dataclass(frozen=True, slots=True)
class PreparedPositionIndexedTrigrams:
    """
    Trigram statistics prepared for repeated A-Z indexed evaluation.

    records
        Trigrams whose three letters are valid A-Z indexes.

        Each record contains:

            (
                first_letter_index,
                second_letter_index,
                third_letter_index,
                weighted_count,
            )

    permanently_skipped_weight
        Total weight of trigrams that cannot be represented by the
        A-Z indexed fast path.

    evaluated_weight
        Total weight of all prepared trigram records.

        For a complete A-Z layout this value is invariant across
        candidate layouts.
    """

    records: tuple[
        tuple[int, int, int, float],
        ...,
    ]

    permanently_skipped_weight: float
    evaluated_weight: float


class FastTrigramLayoutScoreEvaluator:
    """
    Fast trigram-cost evaluator for exhaustive layout search.

    This evaluator preserves the scoring semantics of
    TrigramLayoutEvaluator while avoiding construction of
    TrigramFeatures, TrigramCost, and TrigramLayoutRecord objects
    for every candidate.

    Structural trigram costs depend only on the three logical
    positions involved. A position-indexed three-dimensional cost
    cube can therefore be built once and reused for all candidates.

    This first implementation intentionally favors correctness and
    a simple hot path over vowel-group-specific optimizations.
    """

    def __init__(
        self,
        weights: TrigramCostWeights,
    ) -> None:
        self._weights = weights

        self._position_cache: dict[
            str,
            LogicalPosition,
        ] = {}

    @property
    def weights(self) -> TrigramCostWeights:
        return self._weights

    def build_cost_cube(
        self,
        position_ids: Sequence[str],
    ) -> TrigramCostCube:
        """
        Build a three-dimensional trigram-cost lookup table.

        The returned cube is indexed as:

            cube[first_position][second_position][third_position]

        Position IDs are parsed only while building the cube.
        Candidate evaluation later uses integer position indexes only.
        """

        positions = tuple(
            self._position(position_id)
            for position_id in position_ids
        )

        position_count = len(positions)

        cube: list[
            tuple[
                tuple[float, ...],
                ...,
            ]
        ] = []

        for first_index in range(position_count):
            first = positions[first_index]

            first_plane: list[
                tuple[float, ...]
            ] = []

            for second_index in range(position_count):
                second = positions[second_index]

                second_row = tuple(
                    self._calculate_cost(
                        first,
                        second,
                        positions[third_index],
                    )
                    for third_index in range(position_count)
                )

                first_plane.append(second_row)

            cube.append(tuple(first_plane))

        return tuple(cube)

    def prepare_position_indexed_trigrams(
        self,
        statistics: TrigramStatistics,
    ) -> PreparedPositionIndexedTrigrams:
        """
        Convert trigram statistics to compact A-Z integer records.

        This work is performed once before repeated candidate
        evaluation.
        """

        records: list[
            tuple[int, int, int, float]
        ] = []

        permanently_skipped_weight = 0.0
        evaluated_weight = 0.0

        for (
            first,
            second,
            third,
            _raw_count,
            weighted_count,
        ) in statistics.evaluation_records():
            first_index = self._letter_index(first)
            second_index = self._letter_index(second)
            third_index = self._letter_index(third)

            if (
                first_index < 0
                or second_index < 0
                or third_index < 0
            ):
                permanently_skipped_weight += (
                    weighted_count
                )
                continue

            records.append(
                (
                    first_index,
                    second_index,
                    third_index,
                    weighted_count,
                )
            )

            evaluated_weight += weighted_count

        return PreparedPositionIndexedTrigrams(
            records=tuple(records),
            permanently_skipped_weight=(
                permanently_skipped_weight
            ),
            evaluated_weight=evaluated_weight,
        )

    def evaluate_prepared_position_indexed_complete(
        self,
        position_indexes: Sequence[int],
        cost_cube: TrigramCostCube,
        prepared: PreparedPositionIndexedTrigrams,
    ) -> FastTrigramLayoutScore:
        """
        Evaluate a complete A-Z layout using prepared trigram records.

        position_indexes must contain exactly 26 entries, where
        element N is the logical-position index occupied by the
        corresponding A-Z letter.

        This complete-layout hot path assumes that every A-Z letter
        has a valid non-negative position index.
        """

        if len(position_indexes) != 26:
            raise ValueError(
                "position_indexes must contain exactly 26 entries"
            )

        positions = position_indexes
        cube = cost_cube

        total_cost = 0.0

        for (
            first_index,
            second_index,
            third_index,
            weighted_count,
        ) in prepared.records:
            first_plane = cube[
                positions[first_index]
            ]

            second_row = first_plane[
                positions[second_index]
            ]

            total_cost += (
                second_row[
                    positions[third_index]
                ]
                * weighted_count
            )

        return FastTrigramLayoutScore(
            total_cost=total_cost,
            evaluated_weight=prepared.evaluated_weight,
            skipped_weight=(
                prepared.permanently_skipped_weight
            ),
        )

    def evaluate_prepared_position_indexed_complete_total_cost(
        self,
        position_indexes: Sequence[int],
        cost_cube: TrigramCostCube,
        prepared: PreparedPositionIndexedTrigrams,
    ) -> float:
        """
        Return only trigram total cost for scalar hot paths.

        evaluated_weight and skipped_weight are invariant across
        complete A-Z candidates and therefore do not need to be
        returned or allocated for every candidate.
        """

        if len(position_indexes) != 26:
            raise ValueError(
                "position_indexes must contain exactly 26 entries"
            )

        positions = position_indexes
        cube = cost_cube

        total_cost = 0.0

        for (
            first_index,
            second_index,
            third_index,
            weighted_count,
        ) in prepared.records:
            first_plane = cube[
                positions[first_index]
            ]

            second_row = first_plane[
                positions[second_index]
            ]

            total_cost += (
                second_row[
                    positions[third_index]
                ]
                * weighted_count
            )

        return total_cost

    @staticmethod
    def _letter_index(
        letter: str,
    ) -> int:
        """
        Convert one ASCII A-Z letter to a zero-based integer index.

        Return -1 for unsupported input.
        """

        if len(letter) != 1:
            return -1

        code = ord(letter.upper())

        if not ord("A") <= code <= ord("Z"):
            return -1

        return code - ord("A")

    def _position(
        self,
        position_id: str,
    ) -> LogicalPosition:
        """
        Return a cached parsed logical position.
        """

        position = self._position_cache.get(
            position_id
        )

        if position is None:
            position = LogicalPositionParser.parse(
                position_id
            )

            self._position_cache[
                position_id
            ] = position

        return position

    def _calculate_cost(
        self,
        first: LogicalPosition,
        second: LogicalPosition,
        third: LogicalPosition,
    ) -> float:
        """
        Calculate trigram cost directly from three logical positions.

        The formula intentionally mirrors:

            TrigramEvaluator
                -> TrigramCostEvaluator

        This method is used only while building the position-cost
        cube. It is not part of the per-candidate hot loop.
        """

        first_second_same_hand = (
            first.hand is second.hand
        )

        second_third_same_hand = (
            second.hand is third.hand
        )

        first_third_same_hand = (
            first.hand is third.hand
        )

        first_second_same_finger = (
            first_second_same_hand
            and first.finger is second.finger
        )

        second_third_same_finger = (
            second_third_same_hand
            and second.finger is third.finger
        )

        first_third_same_finger = (
            first_third_same_hand
            and first.finger is third.finger
        )

        same_finger_skip = (
            first_third_same_finger
            and not first_second_same_finger
            and not second_third_same_finger
        )

        alternating_hands = (
            first.hand is third.hand
            and first.hand is not second.hand
        )

        same_hand = (
            first.hand is second.hand
            and second.hand is third.hand
        )

        same_hand_same_finger_skip = (
            same_finger_skip
            and same_hand
        )

        first_roll = self._roll_direction(
            first,
            second,
        )

        second_roll = self._roll_direction(
            second,
            third,
        )

        roll_direction = RollDirection.NONE
        redirect = False

        if (
            same_hand
            and first_roll is not RollDirection.NONE
            and second_roll is not RollDirection.NONE
        ):
            if first_roll is second_roll:
                roll_direction = first_roll
            else:
                redirect = True

        cost = 0.0

        if same_hand_same_finger_skip:
            cost += (
                self._weights
                .same_finger_skip_penalty
            )
        elif redirect:
            cost += (
                self._weights.redirect_penalty
            )

        if alternating_hands:
            cost -= (
                self._weights.alternation_reward
            )

        if roll_direction is RollDirection.INWARD:
            cost -= (
                self._weights.inward_roll_reward
            )
        elif roll_direction is RollDirection.OUTWARD:
            cost -= (
                self._weights.outward_roll_reward
            )

        return cost

    @staticmethod
    def _roll_direction(
        source: LogicalPosition,
        target: LogicalPosition,
    ) -> RollDirection:
        """
        Determine adjacent-finger roll direction.

        This mirrors the existing two-key roll semantics used by
        TrigramEvaluator through RollDetector.
        """

        if source.hand is not target.hand:
            return RollDirection.NONE

        if source.finger is target.finger:
            return RollDirection.NONE

        source_index = _FINGER_ORDER.get(
            source.finger.name
        )

        target_index = _FINGER_ORDER.get(
            target.finger.name
        )

        if (
            source_index is None
            or target_index is None
        ):
            return RollDirection.NONE

        difference = (
            target_index
            - source_index
        )

        if abs(difference) != 1:
            return RollDirection.NONE

        if source.hand is Hand.LEFT:
            inward = difference == 1
        else:
            inward = difference == -1

        if inward:
            return RollDirection.INWARD

        return RollDirection.OUTWARD