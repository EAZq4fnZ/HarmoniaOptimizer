from typing import ClassVar

# models/logical_position_parser.py
from .enums import Finger, Hand, Layer, Row
from .logical_position import LogicalPosition


class LogicalPositionParser:
    """
    Parse a canonical logical position ID into LogicalPosition.

    Canonical format
    ----------------
    HAND-FINGER-ROW-COLUMN

    Examples
    --------
    L-M-H-2
    R-I-T-4
    L-R-B-1
    """

    _HAND_MAP: ClassVar[dict[str, Hand]] = {
        "L": Hand.LEFT,
        "R": Hand.RIGHT,
    }

    _FINGER_MAP: ClassVar[dict[str, Finger]] = {
        "P": Finger.PINKY,
        "R": Finger.RING,
        "M": Finger.MIDDLE,
        "I": Finger.INDEX,
    }

    _ROW_MAP: ClassVar[dict[str, Row]] = {
        "T": Row.TOP,
        "H": Row.HOME,
        "B": Row.BOTTOM,
    }

    @classmethod
    def parse(
        cls,
        position_id: str,
        *,
        layer: Layer = Layer.L0,
    ) -> LogicalPosition:
        """
        Parse a logical position ID.

        Example
        -------
        L-M-H-2

        ->
        LogicalPosition(
            layer=Layer.L0,
            hand=Hand.LEFT,
            finger=Finger.MIDDLE,
            row=Row.HOME,
            column=2,
        )
        """

        parts = position_id.strip().upper().split("-")

        if len(parts) != 4:
            raise ValueError(
                "Logical position ID must use "
                "HAND-FINGER-ROW-COLUMN format: "
                f"{position_id!r}"
            )

        hand_code, finger_code, row_code, column_code = parts

        try:
            hand = cls._HAND_MAP[hand_code]
        except KeyError:
            raise ValueError(
                f"Unknown hand code: {hand_code!r}"
            ) from None

        try:
            finger = cls._FINGER_MAP[finger_code]
        except KeyError:
            raise ValueError(
                f"Unknown finger code: {finger_code!r}"
            ) from None

        try:
            row = cls._ROW_MAP[row_code]
        except KeyError:
            raise ValueError(
                f"Unknown row code: {row_code!r}"
            ) from None

        try:
            column = int(column_code)
        except ValueError:
            raise ValueError(
                f"Column must be an integer: {column_code!r}"
            ) from None

        if column < 0:
            raise ValueError(
                f"Column must be zero or greater: {column}"
            )

        return LogicalPosition(
            layer=layer,
            hand=hand,
            finger=finger,
            row=row,
            column=column,
        )

