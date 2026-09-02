from __future__ import annotations

import argparse
import sys
from pathlib import Path

from app.optimization_app import OptimizationApp
from config_loader.constraint_config_loader import (
    ConstraintConfigLoader,
)
from config_loader.optimization_config_loader import (
    OptimizationConfigLoader,
)
from config_loader.search_budget_profiles_loader import (
    SearchBudgetProfilesLoader,
)
from file_digest import sha256_file
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry
from models.layout import Layout
from models.search_mode import SearchMode
from result_serializer import (
    serialize_best_result,
    write_result_json,
)

OPTIMIZATION_CONFIG_PATH = Path(
    "config/optimization/default.json"
)
CONSTRAINT_CONFIG_PATH = Path(
    "config/constraints/default.json"
)
SEARCH_CONFIG_PATH = Path(
    "config/search/default.json"
)
POSITION_COSTS_PATH = Path(
    "config/harmonia_position_costs.py"
)


def parse_args(
    argv: list[str] | None = None,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Optimize a Harmonia keyboard layout."
    )

    parser.add_argument(
        "--layout",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--corpus",
        type=Path,
        required=True,
    )

    parser.add_argument(
        "--mode",
        type=SearchMode,
        choices=list(SearchMode),
        default=SearchMode.STANDARD,
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=20260901,
    )

    parser.add_argument(
        "--output",
        type=Path,
    )

    return parser.parse_args(argv)


def load_corpus(path: Path) -> Corpus:
    text = path.read_text(
        encoding="utf-8"
    )

    return Corpus(
        entries=(
            CorpusEntry(text),
        )
    )


def main() -> int:
    args = parse_args()

    if not args.layout.is_file():
        print(
            f"error: layout file not found: {args.layout}",
            file=sys.stderr,
        )
        return 2

    if not args.corpus.is_file():
        print(
            f"error: corpus file not found: {args.corpus}",
            file=sys.stderr,
        )
        return 2

    optimization_config = (
        OptimizationConfigLoader.load(
            OPTIMIZATION_CONFIG_PATH
        )
    )

    constraint_config = (
        ConstraintConfigLoader.load(
            CONSTRAINT_CONFIG_PATH
        )
    )

    search_profiles = (
        SearchBudgetProfilesLoader.load(
            SEARCH_CONFIG_PATH
        )
    )

    layout = Layout.load(
        args.layout
    )

    corpus = load_corpus(
        args.corpus
    )

    app = OptimizationApp(
        config=optimization_config,
        constraint_config=constraint_config,
    )

    result = app.optimize_with_mode(
        layout=layout,
        corpus=corpus,
        mode=args.mode,
        profiles=search_profiles,
        seed=args.seed,
    )

    best = result.best_result

    if best is None:
        print("No valid optimization result.")
        return 1

    print(
        f"mode={args.mode.value}"
    )
    print(
        f"runs={result.run_count}"
    )
    print(
        f"best_score={best.final_score}"
    )

    layout_result = (
        best.final_evaluation.layout
    )

    print("mapping:")

    for letter in sorted(
        layout_result.mapping
    ):
        print(
            f"  {letter}="
            f"{layout_result.mapping[letter]}"
        )

    if args.output is not None:
        budget = search_profiles.for_mode(
            args.mode
        )

        data = serialize_best_result(
            result=result,
            source_layout=layout,
            mode=args.mode,
            seed=args.seed,
            max_iterations=(
                budget.max_iterations
            ),
            corpus_path=args.corpus,
            corpus_sha256=sha256_file(
                args.corpus
            ),
            optimization_config_path=(
                OPTIMIZATION_CONFIG_PATH
            ),
            optimization_config_sha256=(
                sha256_file(
                    OPTIMIZATION_CONFIG_PATH
                )
            ),
            constraint_config_path=(
                CONSTRAINT_CONFIG_PATH
            ),
            constraint_config_sha256=(
                sha256_file(
                    CONSTRAINT_CONFIG_PATH
                )
            ),
            search_config_path=(
                SEARCH_CONFIG_PATH
            ),
            search_config_sha256=sha256_file(
                SEARCH_CONFIG_PATH
            ),
            position_costs_path=(
                POSITION_COSTS_PATH
            ),
            position_costs_sha256=sha256_file(
                POSITION_COSTS_PATH
            ),
        )

        write_result_json(
            path=args.output,
            data=data,
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
