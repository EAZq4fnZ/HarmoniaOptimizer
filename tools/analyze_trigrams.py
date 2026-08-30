# tools/analyze_trigrams.py

from __future__ import annotations

import argparse
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

from evaluator.corpus_analyzer import CorpusAnalyzer
from evaluator.trigram_evaluator import TrigramEvaluator
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry
from models.enums import Finger, RollDirection
from models.layout import Layout
from models.layout_key_mapper import LayoutKeyMapper

_FINGER_ORDER = {
    Finger.PINKY: 0,
    Finger.RING: 1,
    Finger.MIDDLE: 2,
    Finger.INDEX: 3,
}


@dataclass(slots=True, frozen=True)
class TrigramExample:
    trigram: str
    weighted_count: float
    movement: str


@dataclass(slots=True)
class TrigramDistribution:
    total_weight: float = 0.0

    same_finger_skip: float = 0.0
    same_hand_same_finger_skip: float = 0.0
    alternating_same_finger_skip: float = 0.0

    same_hand_sfs_span_1: float = 0.0
    same_hand_sfs_span_2: float = 0.0
    same_hand_sfs_span_3: float = 0.0

    redirect: float = 0.0
    same_finger_skip_redirect: float = 0.0

    alternation: float = 0.0
    inward_roll: float = 0.0
    outward_roll: float = 0.0

    other: float = 0.0

    same_finger_skip_examples: list[
        TrigramExample
    ] = field(default_factory=list)

    same_hand_same_finger_skip_examples: list[
        TrigramExample
    ] = field(default_factory=list)

    alternating_same_finger_skip_examples: list[
        TrigramExample
    ] = field(default_factory=list)

    redirect_examples: list[
        TrigramExample
    ] = field(default_factory=list)

    alternation_examples: list[
        TrigramExample
    ] = field(default_factory=list)

    inward_roll_examples: list[
        TrigramExample
    ] = field(default_factory=list)

    outward_roll_examples: list[
        TrigramExample
    ] = field(default_factory=list)

    other_examples: list[
        TrigramExample
    ] = field(default_factory=list)


def _position_label(
    position,
) -> str:
    hand = position.hand.value
    finger = position.finger.value

    return f"{hand}-{finger}"


def _movement_label(
    first_key,
    second_key,
    third_key,
) -> str:
    return " -> ".join(
        (
            _position_label(first_key.position),
            _position_label(second_key.position),
            _position_label(third_key.position),
        )
    )


def analyze(
    layout: Layout,
    corpus: Corpus,
) -> TrigramDistribution:
    statistics = CorpusAnalyzer().analyze_trigrams(
        corpus
    )

    mapper = LayoutKeyMapper(
        layout
    )

    evaluator = TrigramEvaluator()

    distribution = TrigramDistribution()

    for (
        first_id,
        second_id,
        third_id,
        _raw_count,
        weighted_count,
    ) in statistics.evaluation_records():
        if (
            first_id not in layout
            or second_id not in layout
            or third_id not in layout
        ):
            continue

        first_key = mapper.key(first_id)
        second_key = mapper.key(second_id)
        third_key = mapper.key(third_id)

        features = evaluator.evaluate(
            first_key,
            second_key,
            third_key,
        )

        example = TrigramExample(
            trigram=(
                first_id
                + second_id
                + third_id
            ),
            weighted_count=weighted_count,
            movement=_movement_label(
                first_key,
                second_key,
                third_key,
            ),
        )

        distribution.total_weight += weighted_count

        classified = False

        if features.same_finger_skip:
            distribution.same_finger_skip += weighted_count
            distribution.same_finger_skip_examples.append(
                example
            )
            classified = True

        if features.same_hand_same_finger_skip:
            distribution.same_hand_same_finger_skip += weighted_count
            distribution.same_hand_same_finger_skip_examples.append(
                example
            )

            first_finger_index = _FINGER_ORDER[
                first_key.position.finger
            ]
            second_finger_index = _FINGER_ORDER[
                second_key.position.finger
            ]

            finger_span = abs(
                first_finger_index
                - second_finger_index
            )

            if finger_span == 1:
                distribution.same_hand_sfs_span_1 += weighted_count
            elif finger_span == 2:
                distribution.same_hand_sfs_span_2 += weighted_count
            elif finger_span == 3:
                distribution.same_hand_sfs_span_3 += weighted_count

        if features.alternating_same_finger_skip:
            distribution.alternating_same_finger_skip += weighted_count
            distribution.alternating_same_finger_skip_examples.append(
                example
            )

        if features.redirect:
            distribution.redirect += weighted_count
            distribution.redirect_examples.append(
                example
            )
            classified = True

        if (
            features.same_finger_skip
            and features.redirect
        ):
            distribution.same_finger_skip_redirect += (
                weighted_count
            )

        if features.alternating_hands:
            distribution.alternation += weighted_count
            distribution.alternation_examples.append(
                example
            )
            classified = True

        if (
            features.roll_direction
            is RollDirection.INWARD
        ):
            distribution.inward_roll += weighted_count
            distribution.inward_roll_examples.append(
                example
            )
            classified = True

        elif (
            features.roll_direction
            is RollDirection.OUTWARD
        ):
            distribution.outward_roll += weighted_count
            distribution.outward_roll_examples.append(
                example
            )
            classified = True

        if not classified:
            distribution.other += weighted_count
            distribution.other_examples.append(
                example
            )

    return distribution


def percentage(
    value: float,
    total: float,
) -> float:
    if total == 0.0:
        return 0.0

    return value / total * 100.0


def format_row(
    label: str,
    value: float,
    total: float,
) -> str:
    return (
        f"{label:<24}"
        f"{value:>12.2f}"
        f"{percentage(value, total):>10.2f}%"
    )


def _top_examples(
    examples: list[TrigramExample],
    limit: int,
) -> list[TrigramExample]:
    return sorted(
        examples,
        key=lambda example: (
            -example.weighted_count,
            example.trigram,
        ),
    )[:limit]


def _format_examples(
    label: str,
    examples: list[TrigramExample],
    limit: int,
) -> list[str]:
    lines = [
        "",
        label,
        "-" * len(label),
    ]

    selected = _top_examples(
        examples,
        limit,
    )

    if not selected:
        lines.append("  (none)")
        return lines

    for example in selected:
        lines.append(
            f"  {example.trigram:<5}"
            f"{example.weighted_count:>8.2f}   "
            f"{example.movement}"
        )

    return lines


def format_report(
    layout: Layout,
    distribution: TrigramDistribution,
    *,
    example_limit: int = 10,
) -> str:
    total = distribution.total_weight

    lines = [
        f"Layout: {layout.name}",
        f"Version: {layout.version}",
        "",
        (
            "Total weighted trigram weight: "
            f"{total:.2f}"
        ),
        "",
        "Structural distribution",
        (
            f"{'Category':<24}"
            f"{'Weight':>12}"
            f"{'Percent':>11}"
        ),
        "-" * 47,
        format_row(
            "Same-finger skip",
            distribution.same_finger_skip,
            total,
        ),
        format_row(
            "  Same-hand SFS",
            distribution.same_hand_same_finger_skip,
            total,
        ),
        format_row(
            "    Finger span 1",
            distribution.same_hand_sfs_span_1,
            total,
        ),
        format_row(
            "    Finger span 2",
            distribution.same_hand_sfs_span_2,
            total,
        ),
        format_row(
            "    Finger span 3",
            distribution.same_hand_sfs_span_3,
            total,
        ),
        format_row(
            "  Alternating-hand SFS",
            distribution.alternating_same_finger_skip,
            total,
        ),
        format_row(
            "Redirect",
            distribution.redirect,
            total,
        ),
        format_row(
            "SFS + redirect",
            distribution.same_finger_skip_redirect,
            total,
        ),
        format_row(
            "Alternation",
            distribution.alternation,
            total,
        ),
        format_row(
            "Inward roll",
            distribution.inward_roll,
            total,
        ),
        format_row(
            "Outward roll",
            distribution.outward_roll,
            total,
        ),
        format_row(
            "Other",
            distribution.other,
            total,
        ),
        "",
        (
            "Top examples "
            f"(up to {example_limit} per category)"
        ),
    ]

    lines.extend(
        _format_examples(
            "Same-finger skip",
            distribution.same_finger_skip_examples,
            example_limit,
        )
    )

    lines.extend(
        _format_examples(
            "Same-hand SFS",
            distribution.same_hand_same_finger_skip_examples,
            example_limit,
        )
    )

    lines.extend(
        _format_examples(
            "Alternating-hand SFS",
            distribution.alternating_same_finger_skip_examples,
            example_limit,
        )
    )

    lines.extend(
        _format_examples(
            "Redirect",
            distribution.redirect_examples,
            example_limit,
        )
    )

    lines.extend(
        _format_examples(
            "Alternation",
            distribution.alternation_examples,
            example_limit,
        )
    )

    lines.extend(
        _format_examples(
            "Inward roll",
            distribution.inward_roll_examples,
            example_limit,
        )
    )

    lines.extend(
        _format_examples(
            "Outward roll",
            distribution.outward_roll_examples,
            example_limit,
        )
    )

    lines.extend(
        _format_examples(
            "Other",
            distribution.other_examples,
            example_limit,
        )
    )

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze weighted trigram ergonomic "
            "distribution for a keyboard layout."
        ),
    )

    parser.add_argument(
        "layout",
        type=Path,
        help="Path to the layout JSON file.",
    )

    parser.add_argument(
        "corpus",
        type=Path,
        help="Path to the UTF-8 corpus text file.",
    )

    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help=(
            "Number of example trigrams to show "
            "per category (default: 10)."
        ),
    )

    return parser


def run(
    layout_path: Path,
    corpus_path: Path,
    *,
    example_limit: int = 10,
) -> str:
    if example_limit < 0:
        raise ValueError(
            "example limit must be non-negative"
        )

    layout = Layout.load(
        layout_path
    )

    text = corpus_path.read_text(
        encoding="utf-8"
    )

    if not text.strip():
        raise ValueError(
            "corpus file must not be empty"
        )

    corpus = Corpus(
        entries=(
            CorpusEntry(
                text=text,
            ),
        )
    )

    distribution = analyze(
        layout,
        corpus,
    )

    return format_report(
        layout,
        distribution,
        example_limit=example_limit,
    )


def main(
    argv: Sequence[str] | None = None,
) -> int:
    parser = build_parser()

    args = parser.parse_args(
        argv
    )

    try:
        report = run(
            layout_path=args.layout,
            corpus_path=args.corpus,
            example_limit=args.top,
        )
    except (
        OSError,
        ValueError,
        KeyError,
    ) as exc:
        parser.error(
            str(exc)
        )

    print(report)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
