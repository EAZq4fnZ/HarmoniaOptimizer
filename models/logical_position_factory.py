# models/logical_position_factory.py
from .enums import Finger, Hand, Layer, Row
from .logical_position import LogicalPosition


class LogicalPositionFactory:
    """Create LogicalPosition instances from layout components."""

    @staticmethod
    def create(
        *,
        layer: Layer,
        hand: Hand,
        finger: Finger,
        row: Row,
        column: int,
    ) -> LogicalPosition:
        return LogicalPosition(
            layer=layer,
            hand=hand,
            finger=finger,
            row=row,
            column=column,
        )