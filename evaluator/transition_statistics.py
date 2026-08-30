# evaluator/transition_statistics.py

from __future__ import annotations

from collections import Counter

TransitionRecord = tuple[
    str,
    str,
    int,
    float,
]

IndexedTransitionRecord = tuple[
    int,
    int,
    int,
    float,
]


def _character_index(
    character: str,
) -> int:
    """
    Convert an ASCII letter to its A-Z index.

    A -> 0
    B -> 1
    ...
    Z -> 25

    Non-ASCII-letter IDs return -1.
    """

    if len(character) != 1:
        return -1

    code = ord(
        character.upper()
    )

    if (
        ord("A")
        <= code
        <= ord("Z")
    ):
        return (
            code
            - ord("A")
        )

    return -1


class TransitionStatistics:
    """
    Store raw and weighted transition statistics.

    Evaluation records are cached because the statistics remain
    unchanged while many candidate layouts are evaluated.

    Indexed evaluation records provide a faster A-Z representation
    for exhaustive-search evaluators.

    Affected-transition indexes are also cached so exhaustive-search
    evaluators can efficiently identify only the transitions involving
    a specific A-Z letter.
    """

    def __init__(
        self,
    ) -> None:
        self._raw: Counter[
            tuple[str, str]
        ] = Counter()

        self._weighted: Counter[
            tuple[str, str]
        ] = Counter()

        self._evaluation_records_cache: (
            tuple[
                TransitionRecord,
                ...,
            ]
            | None
        ) = None

        self._indexed_evaluation_records_cache: (
            tuple[
                IndexedTransitionRecord,
                ...,
            ]
            | None
        ) = None

        self._affected_transition_indexes_cache: (
            tuple[
                tuple[int, ...],
                ...,
            ]
            | None
        ) = None

    def add(
        self,
        transitions: dict[
            tuple[str, str],
            int,
        ],
        weight: float = 1.0,
    ) -> None:
        """
        Add transition counts with a weight.
        """

        for (
            transition,
            count,
        ) in transitions.items():
            self._raw[
                transition
            ] += count

            self._weighted[
                transition
            ] += (
                count
                * weight
            )

        self._evaluation_records_cache = None
        self._indexed_evaluation_records_cache = None
        self._affected_transition_indexes_cache = None

    def raw_count(
        self,
        first: str,
        second: str,
    ) -> int:
        """
        Return the raw transition count.
        """

        return self._raw[
            (
                first,
                second,
            )
        ]

    def weighted_count(
        self,
        first: str,
        second: str,
    ) -> float:
        """
        Return the weighted transition count.
        """

        return self._weighted[
            (
                first,
                second,
            )
        ]

    def raw(
        self,
    ) -> dict[
        tuple[str, str],
        int,
    ]:
        """
        Return raw transition counts.
        """

        return dict(
            self._raw
        )

    def weighted(
        self,
    ) -> dict[
        tuple[str, str],
        float,
    ]:
        """
        Return weighted transition counts.
        """

        return dict(
            self._weighted
        )

    def evaluation_records(
        self,
    ) -> tuple[
        TransitionRecord,
        ...,
    ]:
        """
        Return normalized records for repeated layout evaluation.

        Each record contains:

            source uppercase ID
            target uppercase ID
            raw count
            weighted count

        Case variants remain separate records so this preserves
        the existing evaluation semantics.
        """

        cached = (
            self._evaluation_records_cache
        )

        if cached is not None:
            return cached

        records = tuple(
            (
                first.upper(),
                second.upper(),
                self._raw[
                    (
                        first,
                        second,
                    )
                ],
                weighted_count,
            )
            for (
                first,
                second,
            ), weighted_count in (
                self._weighted.items()
            )
        )

        self._evaluation_records_cache = (
            records
        )

        return records

    def indexed_evaluation_records(
        self,
    ) -> tuple[
        IndexedTransitionRecord,
        ...,
    ]:
        """
        Return cached A-Z indexed transition records.

        Each record contains:

            source letter index
            target letter index
            raw count
            weighted count

        A-Z are represented by 0-25.

        IDs that cannot be represented as a single ASCII
        alphabetic character use -1. Fast evaluators can then
        preserve the normal evaluator's skipped-weight behavior.
        """

        cached = (
            self._indexed_evaluation_records_cache
        )

        if cached is not None:
            return cached

        records = tuple(
            (
                _character_index(
                    first
                ),
                _character_index(
                    second
                ),
                self._raw[
                    (
                        first,
                        second,
                    )
                ],
                weighted_count,
            )
            for (
                first,
                second,
            ), weighted_count in (
                self._weighted.items()
            )
        )

        self._indexed_evaluation_records_cache = (
            records
        )

        return records

    def affected_transition_indexes_by_letter(
        self,
    ) -> tuple[
        tuple[int, ...],
        ...,
    ]:
        """
        Return cached transition indexes affected by each A-Z letter.

        The returned tuple contains 26 entries:

            index 0  -> transitions involving A
            index 1  -> transitions involving B
            ...
            index 25 -> transitions involving Z

        A transition is included when the letter appears as either
        its source or target.

        A self-transition such as A -> A is included only once in
        A's transition-index tuple.

        Transitions containing non-A-Z character IDs are ignored for
        the unsupported side, while the valid A-Z side is still indexed.
        """

        cached = (
            self._affected_transition_indexes_cache
        )

        if cached is not None:
            return cached

        affected: list[
            list[int]
        ] = [
            []
            for _ in range(26)
        ]

        for (
            transition_index,
            record,
        ) in enumerate(
            self.indexed_evaluation_records()
        ):
            (
                source_index,
                target_index,
                _raw_count,
                _weighted_count,
            ) = record

            if (
                0
                <= source_index
                < 26
            ):
                affected[
                    source_index
                ].append(
                    transition_index
                )

            if (
                0
                <= target_index
                < 26
                and target_index
                != source_index
            ):
                affected[
                    target_index
                ].append(
                    transition_index
                )

        result = tuple(
            tuple(
                indexes
            )
            for indexes in affected
        )

        self._affected_transition_indexes_cache = (
            result
        )

        return result

    def clear(
        self,
    ) -> None:
        """
        Clear all statistics.
        """

        self._raw.clear()
        self._weighted.clear()

        self._evaluation_records_cache = None
        self._indexed_evaluation_records_cache = None
        self._affected_transition_indexes_cache = None