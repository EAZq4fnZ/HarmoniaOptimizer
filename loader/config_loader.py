# loader/config_loader.py
from pathlib import Path

import json5

from models.geometry import (
    Angles,
    Geometry,
    Origin,
    PositiveDirection,
    Spacing,
    Stagger,
    Transform,
)
from models.keyboard import Keyboard


class ConfigLoader:
    def __init__(self, config_root: Path):
        self.config_root = config_root

    def load_jsonc(self, path: Path) -> dict:
        with path.open("r", encoding="utf-8") as f:
            return json5.load(f)

    def load_keyboard(self, keyboard_name: str) -> Keyboard:
        data = self.load_jsonc(
            self.config_root
            / "keyboards"
            / f"{keyboard_name}.jsonc"
        )

        g = data["geometry"]

        spacing = Spacing(
            column_pitch=g["spacing"]["column_pitch"],
            row_pitch=g["spacing"]["row_pitch"],
        )

        positive = PositiveDirection(
            x=g["origin"]["positive"]["x"],
            y=g["origin"]["positive"]["y"],
            z=g["origin"]["positive"]["z"],
        )

        origin = Origin(
            type=g["origin"]["type"],
            positive=positive,
        )

        stagger = Stagger(
            column=g["stagger"]["column"],
        )

        angles = Angles(
            splay=g["transform"]["angles"]["splay"],
            tenting=g["transform"]["angles"]["tenting"],
            rotation=g["transform"]["angles"]["rotation"],
        )

        transform = Transform(
            angles=angles,
        )

        geometry = Geometry(
            spacing=spacing,
            origin=origin,
            stagger=stagger,
            transform=transform,
        )

        return Keyboard(
            name=data["name"],
            description=data.get("description", ""),
            matrix_id=data["matrix_id"],
            geometry=geometry,
        )