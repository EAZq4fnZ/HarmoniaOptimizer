# main.py

from __future__ import annotations

import argparse
from pathlib import Path
from collections.abc import Sequence

from app.optimization_app import OptimizationApp
from models.layout import Layout


def build_parser() -> argparse.ArgumentParser:
    """
    Build the command-line argument parser.
    """

    parser = argparse.ArgumentParser(
        prog="harmonia-optimizer",
        description=(
            "Optimize a keyboard layout against "
            "a text corpus."
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
        "--max-iterations",
        type=int,
        default=10,
        help=(
            "Maximum number of accepted optimization "
            "iterations (default: 10)."
        ),
    )

    return parser


def run(
    layout_path: Path,
    corpus_path: Path,
    max_iterations: int,
) -> str:
    """
    Run one optimization and return its formatted report.
    """

    if max_iterations < 0:
        raise ValueError(
            "max_iterations must be greater than or equal to 0"
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

    app = OptimizationApp(
        max_iterations=max_iterations,
    )

    result = app.optimize_text(
        layout=layout,
        text=text,
    )

    return app.format_result(
        result
    )


def main(
    argv: Sequence[str] | None = None,
) -> int:
    """
    Command-line entry point.
    """

    parser = build_parser()

    args = parser.parse_args(
        argv
    )

    try:
        report = run(
            layout_path=args.layout,
            corpus_path=args.corpus,
            max_iterations=args.max_iterations,
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