# config_loader/constraint_config_loader.py

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from models.constraint_config import (
    ConstraintConfig,
    ForbiddenPositionConstraintConfig,
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
        vowel_data = data["vowel_position"]
        forbidden_data = data["forbidden_position"]

        return ConstraintConfig(
            version=str(data["version"]),
            vowel_position=VowelPositionConstraintConfig(
                enabled=bool(
                    vowel_data["enabled"]
                ),
                allowed_positions=frozenset(
                    str(position)
                    for position in vowel_data[
                        "allowed_positions"
                    ]
                ),
            ),
            forbidden_position=(
                ForbiddenPositionConstraintConfig(
                    enabled=bool(
                        forbidden_data["enabled"]
                    ),
                    forbidden_positions=frozenset(
                        str(position)
                        for position in forbidden_data[
                            "forbidden_positions"
                        ]
                    ),
                )
            ),
        )