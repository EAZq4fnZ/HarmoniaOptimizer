from __future__ import annotations

from pathlib import Path

from config.harmonia_position_costs import (
    make_harmonia_position_cost_profile,
)
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
from evaluator.key_position_evaluator import (
    KeyPositionEvaluator,
)
from evaluator.layout_evaluator import LayoutEvaluator
from evaluator.trigram_layout_evaluator import (
    TrigramLayoutEvaluator,
)
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry
from models.layout import Layout

ROOT = Path(__file__).resolve().parents[1]


LAYOUTS = [
    "harmonia_v5_1b.json",
    "harmonia_v5_1b_vowels_balanced_seed.json",
    "harmonia_v5_1b_vowels_left_seed.json",
    "harmonia_v5_1b_vowels_split_seed.json",
]


def load_text() -> str:
    corpus_path = ROOT / "corpus" / "sample.txt"

    if corpus_path.exists():
        return corpus_path.read_text(
            encoding="utf-8"
        )

    return (
        "konnichiwa watashi no namae wa harmonia desu "
        "this is a small temporary corpus for diagnostics "
        "typescript python rust javascript keyboard layout"
    )


def make_evaluator() -> CandidateEvaluator:
    config = OptimizationConfigLoader.load(
        ROOT / "config/optimization/default.json"
    )

    constraints = ConstraintConfigLoader.load(
        ROOT / "config/constraints/default.json"
    )

    return CandidateEvaluator(
        constraint_set=ConstraintFactory.create(
            constraints
        ),
        layout_evaluator=LayoutEvaluator(
            config.transition_cost_weights
        ),
        finger_load_pipeline=FingerLoadPipeline(),
        candidate_scorer=CandidateScorer(
            config.candidate_score_weights
        ),
        finger_load_budgets=config.finger_load_budgets,
        trigram_layout_evaluator=TrigramLayoutEvaluator(
            config.trigram_cost_weights
        ),
        key_position_evaluator=KeyPositionEvaluator(
            make_harmonia_position_cost_profile()
        ),
    )


def evaluate_layout(name: str):
    layout = Layout.load(
        ROOT / "config/layouts" / name
    )

    corpus = Corpus(
        entries=(
            CorpusEntry(load_text()),
        )
    )

    analyzer = CorpusAnalyzer()

    transition = analyzer.analyze(corpus)
    trigram = analyzer.analyze_trigrams(corpus)
    characters = CharacterAnalyzer().analyze(corpus)

    evaluation = make_evaluator().evaluate(
        layout=layout,
        transition_statistics=transition,
        character_statistics=characters,
        trigram_statistics=trigram,
    )

    score = evaluation.candidate_score

    return {
        "layout": name.replace(".json", ""),
        "transition": score.transition_score,
        "trigram": score.trigram_score,
        "finger": score.finger_load_score,
        "position": score.position_score,
        "total": score.total,
    }


def main():
    rows = [
        evaluate_layout(name)
        for name in LAYOUTS
    ]

    print(
        f"{'layout':36}"
        f"{'trans':>9}"
        f"{'tri':>9}"
        f"{'finger':>9}"
        f"{'pos':>9}"
        f"{'total':>9}"
    )

    print("-" * 81)

    for row in rows:
        print(
            f"{row['layout'][:35]:36}"
            f"{row['transition']:9.3f}"
            f"{row['trigram']:9.3f}"
            f"{row['finger']:9.3f}"
            f"{row['position']:9.3f}"
            f"{row['total']:9.3f}"
        )

    print("\nComponent statistics")
    print("-" * 42)

    for key in (
        "transition",
        "trigram",
        "finger",
        "position",
    ):
        values = [
            row[key]
            for row in rows
        ]

        mean = sum(values) / len(values)

        print(
            f"{key:11}"
            f" min={min(values):6.3f}"
            f" mean={mean:6.3f}"
            f" max={max(values):6.3f}"
            f" range={max(values)-min(values):6.3f}"
        )


if __name__ == "__main__":
    main()
