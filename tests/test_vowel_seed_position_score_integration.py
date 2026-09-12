from __future__ import annotations

from config.harmonia_position_costs import (
    make_harmonia_position_cost_profile,
)
from evaluator.candidate_evaluator import CandidateEvaluator
from evaluator.candidate_scorer import CandidateScorer
from evaluator.character_analyzer import CharacterAnalyzer
from evaluator.constraint_factory import ConstraintFactory
from evaluator.corpus_analyzer import CorpusAnalyzer
from evaluator.fast_candidate_evaluator import (
    FastCandidateEvaluator,
)
from evaluator.fast_candidate_scorer import FastCandidateScorer
from evaluator.fast_finger_load_score_evaluator import (
    FastFingerLoadScoreEvaluator,
)
from evaluator.fast_key_position_score_evaluator import (
    FastKeyPositionScoreEvaluator,
)
from evaluator.fast_layout_score_evaluator import (
    FastLayoutScoreEvaluator,
)
from evaluator.finger_load_pipeline import FingerLoadPipeline
from evaluator.key_position_evaluator import KeyPositionEvaluator
from evaluator.layout_evaluator import LayoutEvaluator
from models.candidate_score import CandidateScoreWeights
from models.constraint_config import (
    ConstraintConfig,
    ForbiddenPositionConstraintConfig,
    VowelPositionConstraintConfig,
)
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry
from models.enums import Finger, Hand
from models.finger_load_budget import FingerLoadBudget
from models.layout import Layout
from models.transition_cost import TransitionCostWeights
from optimizer.vowel_seed_builder import VowelSeedBuilder


def make_layout() -> Layout:
    return Layout(
        name="Position score vowel seed regression",
        version="1.0",
        layer="L0",
        description="Regression fixture",
        mapping={
            "A": "L-M-H-2",
            "B": "R-R-T-1",
            "C": "L-I-B-3",
            "D": "R-M-H-2",
            "E": "R-I-T-3",
            "F": "L-P-H-0",
            "G": "R-I-B-3",
            "H": "R-I-H-3",
            "I": "L-I-H-3",
            "J": "R-I-B-4",
            "K": "L-I-T-4",
            "L": "L-R-H-1",
            "M": "R-R-H-1",
            "N": "R-I-H-4",
            "O": "L-I-H-4",
            "P": "R-M-T-2",
            "Q": "R-R-B-1",
            "R": "L-I-T-3",
            "S": "L-I-B-4",
            "T": "L-M-T-2",
            "U": "R-I-T-4",
            "V": "L-M-B-2",
            "W": "L-R-B-1",
            "X": "R-M-B-2",
            "Y": "L-R-T-1",
            "Z": "R-P-H-0",
        },
    )


def make_constraint_config() -> ConstraintConfig:
    return ConstraintConfig(
        version="1.0",
        vowel_position=VowelPositionConstraintConfig(
            enabled=True,
            allowed_positions=frozenset(
                {
                    "L-R-T-1",
                    "L-M-T-2",
                    "L-I-T-3",
                    "L-I-T-4",
                    "L-R-H-1",
                    "L-M-H-2",
                    "L-I-H-3",
                    "L-I-H-4",
                }
            ),
        ),
        forbidden_position=ForbiddenPositionConstraintConfig(
            enabled=False,
            forbidden_positions=frozenset(),
        ),
    )


def make_transition_weights() -> TransitionCostWeights:
    return TransitionCostWeights(
        same_finger_penalty=10.0,
        same_hand_penalty=2.0,
        row_change_penalty=1.5,
        alternation_reward=2.0,
        inward_roll_reward=1.5,
        outward_roll_reward=0.5,
    )


def make_finger_load_budgets() -> tuple[FingerLoadBudget, ...]:
    result: list[FingerLoadBudget] = []

    for hand in (Hand.LEFT, Hand.RIGHT):
        result.extend(
            (
                FingerLoadBudget(
                    hand=hand,
                    finger=Finger.INDEX,
                    target_ratio=0.25,
                    tolerance=0.05,
                ),
                FingerLoadBudget(
                    hand=hand,
                    finger=Finger.MIDDLE,
                    target_ratio=0.15,
                    tolerance=0.05,
                ),
                FingerLoadBudget(
                    hand=hand,
                    finger=Finger.RING,
                    target_ratio=0.07,
                    tolerance=0.03,
                ),
                FingerLoadBudget(
                    hand=hand,
                    finger=Finger.PINKY,
                    target_ratio=0.03,
                    tolerance=0.02,
                ),
            )
        )

    return tuple(result)


def make_candidate_weights() -> CandidateScoreWeights:
    return CandidateScoreWeights(
        transition_weight=0.0,
        trigram_weight=0.0,
        finger_load_weight=0.0,
        position_weight=1.0,
    )


def make_normal_evaluator() -> CandidateEvaluator:
    return CandidateEvaluator(
        constraint_set=ConstraintFactory.create(
            make_constraint_config()
        ),
        layout_evaluator=LayoutEvaluator(
            make_transition_weights()
        ),
        finger_load_pipeline=FingerLoadPipeline(),
        candidate_scorer=CandidateScorer(
            make_candidate_weights()
        ),
        finger_load_budgets=make_finger_load_budgets(),
        key_position_evaluator=KeyPositionEvaluator(
            make_harmonia_position_cost_profile()
        ),
    )


def make_fast_evaluator() -> FastCandidateEvaluator:
    return FastCandidateEvaluator(
        constraint_set=ConstraintFactory.create(
            make_constraint_config()
        ),
        layout_evaluator=FastLayoutScoreEvaluator(
            make_transition_weights()
        ),
        finger_load_evaluator=FastFingerLoadScoreEvaluator(
            make_finger_load_budgets()
        ),
        candidate_scorer=FastCandidateScorer(
            make_candidate_weights()
        ),
        key_position_evaluator=FastKeyPositionScoreEvaluator(
            make_harmonia_position_cost_profile()
        ),
    )


def test_fast_vowel_seed_matches_normal_when_position_score_is_enabled(
) -> None:
    corpus = Corpus(
        entries=(
            CorpusEntry(
                text=(
                    "AAAAAAAAAAAAAAAAAAAA "
                    "EEEEEEEEEEEEEEE "
                    "IIIIIIIIII "
                    "OOOOO "
                    "U"
                ),
            ),
        )
    )

    corpus_analyzer = CorpusAnalyzer()

    transition_statistics = corpus_analyzer.analyze(
        corpus
    )
    character_statistics = CharacterAnalyzer().analyze(
        corpus
    )

    constraint_config = make_constraint_config()
    layout = make_layout()

    normal_builder = VowelSeedBuilder(
        evaluator=make_normal_evaluator(),
        allowed_positions=(
            constraint_config.vowel_position.allowed_positions
        ),
    )

    fast_builder = VowelSeedBuilder(
        evaluator=make_normal_evaluator(),
        fast_evaluator=make_fast_evaluator(),
        allowed_positions=(
            constraint_config.vowel_position.allowed_positions
        ),
    )

    normal_result = normal_builder.build(
        layout=layout,
        transition_statistics=transition_statistics,
        character_statistics=character_statistics,
    )

    fast_result = fast_builder.build(
        layout=layout,
        transition_statistics=transition_statistics,
        character_statistics=character_statistics,
    )

    assert fast_result.score == normal_result.score

    for vowel in "AEIOU":
        assert (
            fast_result.layout.position(vowel)
            == normal_result.layout.position(vowel)
        )
