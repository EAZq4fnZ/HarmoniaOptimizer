# optimizer/layout_mutator.py

from __future__ import annotations

from models.layout import Layout


class LayoutMutator:
    """
    Create modified keyboard layouts.

    The original layout is never modified.
    """

    def swap(
        self,
        layout: Layout,
        letter1: str,
        letter2: str,
    ) -> Layout:
        """
        Return a new layout with two letters swapped.

        Example
        -------
        Before:

            A -> L-I-H-3
            B -> R-I-H-3

        After swap(A, B):

            A -> R-I-H-3
            B -> L-I-H-3
        """

        letter1 = letter1.upper()
        letter2 = letter2.upper()

        if letter1 not in layout:
            raise KeyError(
                f"Unknown letter: {letter1}"
            )

        if letter2 not in layout:
            raise KeyError(
                f"Unknown letter: {letter2}"
            )

        mapping = dict(layout.mapping)

        mapping[letter1], mapping[letter2] = (
            mapping[letter2],
            mapping[letter1],
        )

        return Layout(
            name=layout.name,
            version=layout.version,
            layer=layout.layer,
            description=layout.description,
            mapping=mapping,
        )