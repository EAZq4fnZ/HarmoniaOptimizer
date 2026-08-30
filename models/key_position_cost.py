from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True, slots=True)
class KeyPositionCostProfile:
    """
    Ergonomic costs assigned to canonical logical-position IDs.

    Lower cost is better.
    """

    costs: Mapping[str, float]

    def __post_init__(self) -> None:
        normalized: dict[str, float] = {}

        for position_id, cost in self.costs.items():
            canonical_id = position_id.strip().upper()
            numeric_cost = float(cost)

            if not canonical_id:
                raise ValueError(
                    "position ID must not be empty"
                )

            if numeric_cost < 0.0:
                raise ValueError(
                    "key position cost must be non-negative"
                )

            normalized[canonical_id] = numeric_cost

        object.__setattr__(
            self,
            "costs",
            MappingProxyType(normalized),
        )

    def cost(
        self,
        position_id: str,
    ) -> float | None:
        return self.costs.get(
            position_id.strip().upper()
        )
