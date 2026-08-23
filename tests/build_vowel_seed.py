# tools/build_vowel_seed.py

from __future__ import annotations

import argparse
from pathlib import Path

from config_loader.constraint_config_loader import (
    ConstraintConfigLoader,
)
from config_loader.optimization_config_loader import (
    OptimizationConfigLoader,
)
from evaluator.candidate_evaluator import CandidateEvaluator
from evaluator.candidate_scorer import CandidateScorer
from evaluator.character_analyzer import CharacterAnalyzer
from evaluator.constraint_factory import ConstraintFactory
from evaluator.corpus_analyzer import CorpusAnalyzer
from evaluator.finger_load_pipeline import FingerLoadPipeline
from evaluator.layout_evaluator import LayoutEvaluator
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry
from models.layout import Layout
from optimizer.vowel_seed_builder import VowelSeedBuilder


def build_evaluator(
    optimization_config_path: Path,
    constraint_config_path: Path,
) -> CandidateEvaluator:
    optimization_config = OptimizationConfigLoader.load(
        optimization_config_path
    )

    constraint_config = ConstraintConfigLoader.load(
        constraint_config_path
    )

    return CandidateEvaluator(
        constraint_set=ConstraintFactory.create(
            constraint_config
        ),
        layout_evaluator=LayoutEvaluator(
            optimization_config.transition_cost_weights
        ),
        finger_load_pipeline=FingerLoadPipeline(),
        candidate_scorer=CandidateScorer(
            optimization_config.candidate_score_weights
        ),
        finger_load_budgets=(
            optimization_config.finger_load_budgets
        ),
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="build-vowel-seed",
        description=(
            "Build the best valid vowel seed for a layout."
        ),
    )

    parser.add_argument(
        "layout",
        type=Path,
    )

    parser.add_argument(
        "corpus",
        type=Path,
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=Path(
            "config/optimization/default.json"
        ),
    )

    parser.add_argument(
        "--constraints",
        type=Path,
        required=True,
    )

    args = parser.parse_args()

    layout = Layout.load(
        args.layout
    )

    text = args.corpus.read_text(
        encoding="utf-8"
    )

    corpus = Corpus(
        entries=(
            CorpusEntry(
                text=text,
            ),
        ),
    )

    transition_statistics = CorpusAnalyzer().analyze(
        corpus
    )

    character_statistics = CharacterAnalyzer().analyze(
        corpus
    )

    constraint_config = ConstraintConfigLoader.load(
        args.constraints
    )

    evaluator = build_evaluator(
        optimization_config_path=args.config,
        constraint_config_path=args.constraints,
    )

    builder = VowelSeedBuilder(
        evaluator=evaluator,
        allowed_positions=(
            constraint_config
            .vowel_position
            .allowed_positions
        ),
    )

    result = builder.build(
        layout=layout,
        transition_statistics=transition_statistics,
        character_statistics=character_statistics,
    )

    print("Best Vowel Seed")
    print("================")
    print()

    if result.score is None:
        print("Score: N/A")
    else:
        print(
            f"Score: {result.score:.6f}"
        )

    print()
    print("Vowel positions")
    print("---------------")

    for vowel in "AEIOU":
        print(
            f"{vowel}: "
            f"{result.layout.position(vowel)}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())