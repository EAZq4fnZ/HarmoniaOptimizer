# config_loader/constraint_config_loader.py

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from models.constraint_config import (
    ConstraintConfig,
    ForbiddenPositionConstraintConfig,
    VowelHandDistributionConstraintConfig,
    VowelPositionConstraintConfig,
)


class ConstraintConfigLoader:
    @classmethod
    def load(
        cls,
        path: str | Path,
    ) -> ConstraintConfig:
        path = Path(path)

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return cls.from_dict(data)

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> ConstraintConfig:
        vowel_data = data[
            "vowel_position"
        ]

        forbidden_data = data[
            "forbidden_position"
        ]

        distribution_data = data.get(
            "vowel_hand_distribution",
            {
                "enabled": False,
                "min_left_vowels": 0,
                "max_left_vowels": 5,
            },
        )

        return ConstraintConfig(
            version=str(
                data["version"]
            ),
            vowel_position=(
                VowelPositionConstraintConfig(
                    enabled=bool(
                        vowel_data[
                            "enabled"
                        ]
                    ),
                    allowed_positions=frozenset(
                        str(position)
                        for position in vowel_data[
                            "allowed_positions"
                        ]
                    ),
                )
            ),
            forbidden_position=(
                ForbiddenPositionConstraintConfig(
                    enabled=bool(
                        forbidden_data[
                            "enabled"
                        ]
                    ),
                    forbidden_positions=frozenset(
                        str(position)
                        for position in forbidden_data[
                            "forbidden_positions"
                        ]
                    ),
                )
            ),
            vowel_hand_distribution=(
                VowelHandDistributionConstraintConfig(
                    enabled=bool(
                        distribution_data[
                            "enabled"
                        ]
                    ),
                    min_left_vowels=int(
                        distribution_data[
                            "min_left_vowels"
                        ]
                    ),
                    max_left_vowels=int(
                        distribution_data[
                            "max_left_vowels"
                        ]
                    ),
                )
            ),
        )