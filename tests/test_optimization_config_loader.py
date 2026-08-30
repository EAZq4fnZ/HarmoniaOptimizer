# tests/test_optimization_config_loader.py

from __future__ import annotations

import json
from pathlib import Path

import pytest

from config_loader.optimization_config_loader import (
    OptimizationConfigLoader,
)
from models.enums import Finger, Hand
from models.optimization_config import OptimizationConfig


def make_config_dict() -> dict:
    return {
        "version": "1.0",
        "transition_cost_weights": {
            "same_finger_penalty": 10.0,
            "same_hand_penalty": 2.0,
            "row_change_penalty": 1.5,
            "alternation_reward": 2.0,
            "inward_roll_reward": 1.5,
            "outward_roll_reward": 0.5,
        },
        "candidate_score_weights": {
            "transition_weight": 1.0,
            "finger_load_weight": 1.0,
        },
        "finger_load_budgets": [
            {
                "hand": "left",
                "finger": "index",
                "target_ratio": 0.25,
                "tolerance": 0.05,
            },
            {
                "hand": "right",
                "finger": "pinky",
                "target_ratio": 0.03,
                "tolerance": 0.02,
            },
        ],
    }


def test_from_dict_returns_optimization_config():
    config = OptimizationConfigLoader.from_dict(
        make_config_dict()
    )

    assert isinstance(
        config,
        OptimizationConfig,
    )


def test_from_dict_loads_version():
    config = OptimizationConfigLoader.from_dict(
        make_config_dict()
    )

    assert config.version == "1.0"


def test_from_dict_loads_transition_weights():
    config = OptimizationConfigLoader.from_dict(
        make_config_dict()
    )

    weights = config.transition_cost_weights

    assert weights.same_finger_penalty == 10.0
    assert weights.same_hand_penalty == 2.0
    assert weights.row_change_penalty == 1.5
    assert weights.alternation_reward == 2.0
    assert weights.inward_roll_reward == 1.5
    assert weights.outward_roll_reward == 0.5


def test_from_dict_loads_candidate_weights():
    config = OptimizationConfigLoader.from_dict(
        make_config_dict()
    )

    weights = config.candidate_score_weights

    assert weights.transition_weight == 1.0
    assert weights.finger_load_weight == 1.0


def test_from_dict_defaults_trigram_candidate_weight_to_zero():
    config = OptimizationConfigLoader.from_dict(
        make_config_dict()
    )

    assert (
        config.candidate_score_weights.trigram_weight
        == 0.0
    )


def test_from_dict_defaults_trigram_cost_weights_to_zero():
    config = OptimizationConfigLoader.from_dict(
        make_config_dict()
    )

    weights = config.trigram_cost_weights

    assert weights.same_finger_skip_penalty == 0.0
    assert weights.redirect_penalty == 0.0
    assert weights.alternation_reward == 0.0
    assert weights.inward_roll_reward == 0.0
    assert weights.outward_roll_reward == 0.0


def test_from_dict_loads_trigram_candidate_weight():
    data = make_config_dict()

    data["candidate_score_weights"][
        "trigram_weight"
    ] = 2.5

    config = OptimizationConfigLoader.from_dict(
        data
    )

    assert (
        config.candidate_score_weights.trigram_weight
        == 2.5
    )


def test_from_dict_loads_trigram_cost_weights():
    data = make_config_dict()

    data["trigram_cost_weights"] = {
        "same_finger_skip_penalty": 8.0,
        "redirect_penalty": 4.0,
        "alternation_reward": 2.0,
        "inward_roll_reward": 1.5,
        "outward_roll_reward": 0.5,
    }

    config = OptimizationConfigLoader.from_dict(
        data
    )

    weights = config.trigram_cost_weights

    assert weights.same_finger_skip_penalty == 8.0
    assert weights.redirect_penalty == 4.0
    assert weights.alternation_reward == 2.0
    assert weights.inward_roll_reward == 1.5
    assert weights.outward_roll_reward == 0.5


def test_from_dict_loads_finger_load_budgets():
    config = OptimizationConfigLoader.from_dict(
        make_config_dict()
    )

    assert len(config.finger_load_budgets) == 2

    left = config.finger_load_budgets[0]

    assert left.hand == Hand.LEFT
    assert left.finger == Finger.INDEX
    assert left.target_ratio == 0.25
    assert left.tolerance == 0.05

    right = config.finger_load_budgets[1]

    assert right.hand == Hand.RIGHT
    assert right.finger == Finger.PINKY


def test_hand_is_case_insensitive():
    data = make_config_dict()

    data["finger_load_budgets"][0][
        "hand"
    ] = " LEFT "

    config = OptimizationConfigLoader.from_dict(
        data
    )

    assert (
        config.finger_load_budgets[0].hand
        == Hand.LEFT
    )


def test_finger_is_case_insensitive():
    data = make_config_dict()

    data["finger_load_budgets"][0][
        "finger"
    ] = " INDEX "

    config = OptimizationConfigLoader.from_dict(
        data
    )

    assert (
        config.finger_load_budgets[0].finger
        == Finger.INDEX
    )


def test_unknown_hand_is_rejected():
    data = make_config_dict()

    data["finger_load_budgets"][0][
        "hand"
    ] = "center"

    with pytest.raises(
        ValueError,
        match="unknown hand",
    ):
        OptimizationConfigLoader.from_dict(
            data
        )


def test_unknown_finger_is_rejected():
    data = make_config_dict()

    data["finger_load_budgets"][0][
        "finger"
    ] = "unknown"

    with pytest.raises(
        ValueError,
        match="unknown finger",
    ):
        OptimizationConfigLoader.from_dict(
            data
        )


def test_missing_required_key_is_rejected():
    data = make_config_dict()

    del data["transition_cost_weights"][
        "same_finger_penalty"
    ]

    with pytest.raises(KeyError):
        OptimizationConfigLoader.from_dict(
            data
        )


def test_load_reads_json_file(
    tmp_path: Path,
):
    path = tmp_path / "optimization.json"

    path.write_text(
        json.dumps(
            make_config_dict()
        ),
        encoding="utf-8",
    )

    config = OptimizationConfigLoader.load(
        path
    )

    assert config.version == "1.0"

    assert (
        config.transition_cost_weights
        .same_finger_penalty
        == 10.0
    )


def test_load_missing_file_is_rejected(
    tmp_path: Path,
):
    path = (
        tmp_path
        / "missing.json"
    )

    with pytest.raises(
        FileNotFoundError,
    ):
        OptimizationConfigLoader.load(
            path
        )


def test_load_invalid_json_is_rejected(
    tmp_path: Path,
):
    path = tmp_path / "invalid.json"

    path.write_text(
        "{ invalid json",
        encoding="utf-8",
    )

    with pytest.raises(
        json.JSONDecodeError,
    ):
        OptimizationConfigLoader.load(
            path
        )