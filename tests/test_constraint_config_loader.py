# tests/test_constraint_config_loader.py

from __future__ import annotations

import json
from pathlib import Path

import pytest

from config_loader.constraint_config_loader import (
    ConstraintConfigLoader,
)
from models.constraint_config import ConstraintConfig


def make_config_dict() -> dict:
    return {
        "version": "1.0",
        "vowel_position": {
            "enabled": True,
            "allowed_positions": [
                "L-M-H-2",
                "L-I-H-3",
                "R-I-H-3",
            ],
        },
        "forbidden_position": {
            "enabled": True,
            "forbidden_positions": [
                "L-P-T-0",
                "R-P-T-0",
            ],
        },
    }


def test_from_dict_returns_constraint_config():
    config = ConstraintConfigLoader.from_dict(
        make_config_dict()
    )

    assert isinstance(
        config,
        ConstraintConfig,
    )


def test_from_dict_loads_version():
    config = ConstraintConfigLoader.from_dict(
        make_config_dict()
    )

    assert config.version == "1.0"


def test_from_dict_loads_vowel_constraint():
    config = ConstraintConfigLoader.from_dict(
        make_config_dict()
    )

    assert config.vowel_position.enabled is True

    assert config.vowel_position.allowed_positions == frozenset({
        "L-M-H-2",
        "L-I-H-3",
        "R-I-H-3",
    })


def test_from_dict_loads_forbidden_constraint():
    config = ConstraintConfigLoader.from_dict(
        make_config_dict()
    )

    assert (
        config.forbidden_position.enabled
        is True
    )

    assert (
        config.forbidden_position.forbidden_positions
        == frozenset({
            "L-P-T-0",
            "R-P-T-0",
        })
    )


def test_disabled_constraints_are_preserved():
    data = make_config_dict()

    data["vowel_position"]["enabled"] = False

    data["forbidden_position"]["enabled"] = False

    config = ConstraintConfigLoader.from_dict(
        data
    )

    assert (
        config.vowel_position.enabled
        is False
    )

    assert (
        config.forbidden_position.enabled
        is False
    )


def test_missing_required_key_is_rejected():
    data = make_config_dict()

    del data["vowel_position"]

    with pytest.raises(KeyError):
        ConstraintConfigLoader.from_dict(
            data
        )


def test_load_reads_json_file(
    tmp_path: Path,
):
    path = tmp_path / "constraints.json"

    path.write_text(
        json.dumps(
            make_config_dict()
        ),
        encoding="utf-8",
    )

    config = ConstraintConfigLoader.load(
        path
    )

    assert config.version == "1.0"

    assert (
        config.vowel_position.enabled
        is True
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
        ConstraintConfigLoader.load(
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
        ConstraintConfigLoader.load(
            path
        )