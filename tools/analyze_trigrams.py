# tools/analyze_trigrams.py

from __future__ import annotations

import argparse
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from evaluator.corpus_analyzer import CorpusAnalyzer
from evaluator.trigram_evaluator import TrigramEvaluator
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry
from models.enums import RollDirection
from models.layout import Layout
from models.layout_key_mapper import LayoutKeyMapper


@dataclass(slots=True)
class TrigramDistribution:
    total_weight: float = 0.0

    same_finger_skip: float = 0.0
    redirect: float = 0.0
    same_finger_skip_redirect: float = 0.0

    alternation: float = 0.0
    inward_roll: float = 0.0
    outward_roll: float = 0.0

    other: float = 0.0


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

        features = evaluator.evaluate(
            mapper.key(first_id),
            mapper.key(second_id),
            mapper.key(third_id),
        )

        distribution.total_weight += weighted_count

        classified = False

        if features.same_finger_skip:
            distribution.same_finger_skip += weighted_count
            classified = True

        if features.redirect:
            distribution.redirect += weighted_count
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
            classified = True

        if (
            features.roll_direction
            is RollDirection.INWARD
        ):
            distribution.inward_roll += weighted_count
            classified = True

        elif (
            features.roll_direction
            is RollDirection.OUTWARD
        ):
            distribution.outward_roll += weighted_count
            classified = True

        if not classified:
            distribution.other += weighted_count

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


def format_report(
    layout: Layout,
    distribution: TrigramDistribution,
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
    ]

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

    return parser


def run(
    layout_path: Path,
    corpus_path: Path,
) -> str:
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
