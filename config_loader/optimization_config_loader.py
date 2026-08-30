# config_loader/optimization_config_loader.py

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from models.candidate_score import CandidateScoreWeights
from models.enums import Finger, Hand
from models.finger_load_budget import FingerLoadBudget
from models.optimization_config import OptimizationConfig
from models.transition_cost import TransitionCostWeights
from models.trigram_cost import TrigramCostWeights


class OptimizationConfigLoader:
    """
    Load OptimizationConfig from a JSON file.
    """

    @classmethod
    def load(
        cls,
        path: str | Path,
    ) -> OptimizationConfig:
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
    ) -> OptimizationConfig:
        transition_data = data[
            "transition_cost_weights"
        ]

        candidate_data = data[
            "candidate_score_weights"
        ]

        budget_data = data[
            "finger_load_budgets"
        ]

        transition_weights = TransitionCostWeights(
            same_finger_penalty=float(
                transition_data[
                    "same_finger_penalty"
                ]
            ),
            same_hand_penalty=float(
                transition_data[
                    "same_hand_penalty"
                ]
            ),
            row_change_penalty=float(
                transition_data[
                    "row_change_penalty"
                ]
            ),
            alternation_reward=float(
                transition_data[
                    "alternation_reward"
                ]
            ),
            inward_roll_reward=float(
                transition_data[
                    "inward_roll_reward"
                ]
            ),
            outward_roll_reward=float(
                transition_data[
                    "outward_roll_reward"
                ]
            ),
        )

        trigram_data = data.get(
            "trigram_cost_weights"
        )

        if trigram_data is None:
            trigram_weights = TrigramCostWeights()
        else:
            trigram_weights = TrigramCostWeights(
                same_finger_skip_penalty=float(
                    trigram_data[
                        "same_finger_skip_penalty"
                    ]
                ),
                redirect_penalty=float(
                    trigram_data[
                        "redirect_penalty"
                    ]
                ),
                alternation_reward=float(
                    trigram_data[
                        "alternation_reward"
                    ]
                ),
                inward_roll_reward=float(
                    trigram_data[
                        "inward_roll_reward"
                    ]
                ),
                outward_roll_reward=float(
                    trigram_data[
                        "outward_roll_reward"
                    ]
                ),
            )

        candidate_weights = CandidateScoreWeights(
            transition_weight=float(
                candidate_data[
                    "transition_weight"
                ]
            ),
            trigram_weight=float(
                candidate_data.get(
                    "trigram_weight",
                    0.0,
                )
            ),
            finger_load_weight=float(
                candidate_data[
                    "finger_load_weight"
                ]
            ),
        )

        budgets = tuple(
            cls._parse_budget(item)
            for item in budget_data
        )

        return OptimizationConfig(
            version=str(data["version"]),
            transition_cost_weights=transition_weights,
            candidate_score_weights=candidate_weights,
            finger_load_budgets=budgets,
            trigram_cost_weights=trigram_weights,
        )

    @staticmethod
    def _parse_budget(
        data: dict[str, Any],
    ) -> FingerLoadBudget:
        return FingerLoadBudget(
            hand=OptimizationConfigLoader._parse_hand(
                data["hand"]
            ),
            finger=OptimizationConfigLoader._parse_finger(
                data["finger"]
            ),
            target_ratio=float(
                data["target_ratio"]
            ),
            tolerance=float(
                data["tolerance"]
            ),
        )

    @staticmethod
    def _parse_hand(
        value: str,
    ) -> Hand:
        normalized = value.strip().lower()

        mapping = {
            "left": Hand.LEFT,
            "right": Hand.RIGHT,
        }

        try:
            return mapping[normalized]
        except KeyError as exc:
            raise ValueError(
                f"unknown hand: {value}"
            ) from exc

    @staticmethod
    def _parse_finger(
        value: str,
    ) -> Finger:
        normalized = value.strip().lower()

        mapping = {
            "pinky": Finger.PINKY,
            "ring": Finger.RING,
            "middle": Finger.MIDDLE,
            "index": Finger.INDEX,
        }

        try:
            return mapping[normalized]
        except KeyError as exc:
            raise ValueError(
                f"unknown finger: {value}"
            ) from exc