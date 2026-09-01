from __future__ import annotations

from dataclasses import dataclass

from optimizer.multi_start_optimizer import (
    MultiStartOptimizer,
)


@dataclass(frozen=True)
class FakeLayout:
    name: str


@dataclass(frozen=True)
class FakeResult:
    final_score: float | None


class FakeLocalOptimizer:
    def __init__(
        self,
        scores: dict[str, float | None],
    ) -> None:
        self._scores = scores
        self.calls: list[str] = []

    def optimize(
        self,
        layout,
        transition_statistics,
        character_statistics,
        trigram_statistics=None,
    ):
        self.calls.append(layout.name)

        return FakeResult(
            self._scores[layout.name]
        )


class FakeStartLayoutFactory:
    def __init__(
        self,
        layouts: tuple[FakeLayout, ...],
    ) -> None:
        self._layouts = layouts
        self.calls: list[int] = []

    def create(
        self,
        base_layout,
        run_index: int,
    ):
        self.calls.append(run_index)

        return self._layouts[run_index]


def test_rejects_zero_runs() -> None:
    local_optimizer = FakeLocalOptimizer({})
    factory = FakeStartLayoutFactory(())

    try:
        MultiStartOptimizer(
            local_optimizer=local_optimizer,
            start_layout_factory=factory,
            runs=0,
        )
    except ValueError as exc:
        assert (
            str(exc)
            == "runs must be greater than or equal to 1"
        )
    else:
        raise AssertionError(
            "Expected ValueError."
        )


def test_runs_local_search_for_each_start() -> None:
    layouts = (
        FakeLayout("a"),
        FakeLayout("b"),
        FakeLayout("c"),
    )

    local_optimizer = FakeLocalOptimizer(
        {
            "a": 3.0,
            "b": 1.0,
            "c": 2.0,
        }
    )

    factory = FakeStartLayoutFactory(
        layouts
    )

    optimizer = MultiStartOptimizer(
        local_optimizer=local_optimizer,
        start_layout_factory=factory,
        runs=3,
    )

    result = optimizer.optimize(
        layout=FakeLayout("base"),
        transition_statistics=object(),
        character_statistics=object(),
        trigram_statistics=object(),
    )

    assert factory.calls == [0, 1, 2]
    assert local_optimizer.calls == [
        "a",
        "b",
        "c",
    ]

    assert result.run_count == 3
    assert result.best_score == 1.0


def test_passes_statistics_to_local_optimizer() -> None:
    layout = FakeLayout("a")

    received: dict[str, object] = {}

    class RecordingOptimizer:
        def optimize(
            self,
            layout,
            transition_statistics,
            character_statistics,
            trigram_statistics=None,
        ):
            received["layout"] = layout
            received["transition"] = (
                transition_statistics
            )
            received["character"] = (
                character_statistics
            )
            received["trigram"] = (
                trigram_statistics
            )

            return FakeResult(1.0)

    factory = FakeStartLayoutFactory(
        (layout,)
    )

    optimizer = MultiStartOptimizer(
        local_optimizer=RecordingOptimizer(),
        start_layout_factory=factory,
        runs=1,
    )

    transition = object()
    character = object()
    trigram = object()

    optimizer.optimize(
        layout=FakeLayout("base"),
        transition_statistics=transition,
        character_statistics=character,
        trigram_statistics=trigram,
    )

    assert received["layout"] is layout
    assert received["transition"] is transition
    assert received["character"] is character
    assert received["trigram"] is trigram
