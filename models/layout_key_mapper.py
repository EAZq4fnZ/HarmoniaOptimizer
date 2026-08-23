# models/layout_key_mapper.py

from .enums import Layer
from .layout import Layout
from .logical_key import LogicalKey
from .logical_position_parser import LogicalPositionParser


class LayoutKeyMapper:
    """
    Convert layout letter assignments into LogicalKey objects.

    Layout stores:
        A -> "L-M-H-2"

    LayoutKeyMapper converts this into:
        LogicalKey(
            id="A",
            position=LogicalPosition(...),
        )

    LogicalKey objects are cached for the lifetime of this mapper.
    """

    def __init__(
        self,
        layout: Layout,
    ) -> None:
        self._layout = layout
        self._layer = self._parse_layer(
            layout.layer
        )
        self._key_cache: dict[
            str,
            LogicalKey,
        ] = {}

    @staticmethod
    def _parse_layer(
        layer: str,
    ) -> Layer:
        """
        Convert a layout layer string such as "L0"
        into Layer.L0.
        """

        try:
            return Layer[
                layer.upper()
            ]
        except KeyError:
            raise ValueError(
                f"Unknown layout layer: {layer!r}"
            ) from None

    def key(
        self,
        letter: str,
    ) -> LogicalKey:
        """
        Convert a letter in the layout into a LogicalKey.

        Results are cached by normalized letter because a Layout
        is immutable for the lifetime of this mapper.
        """

        normalized_letter = (
            letter.upper()
        )

        cached = self._key_cache.get(
            normalized_letter
        )

        if cached is not None:
            return cached

        position_id = self._layout.position(
            normalized_letter
        )

        position = LogicalPositionParser.parse(
            position_id,
            layer=self._layer,
        )

        key = LogicalKey(
            id=normalized_letter,
            position=position,
        )

        self._key_cache[
            normalized_letter
        ] = key

        return key

    def keys(
        self,
    ) -> tuple[LogicalKey, ...]:
        """
        Return all logical keys in the layout.
        """

        return tuple(
            self.key(letter)
            for letter in self._layout.letters()
        )