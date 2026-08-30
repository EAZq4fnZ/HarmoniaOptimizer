# tests/test_vowel_seed_builder_integration.py

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
from evaluator.fast_layout_score_evaluator import (
    FastLayoutScoreEvaluator,
)
from evaluator.fast_trigram_layout_score_evaluator import (
    FastTrigramLayoutScoreEvaluator,
)
from evaluator.finger_load_pipeline import FingerLoadPipeline
from evaluator.layout_evaluator import LayoutEvaluator
from evaluator.trigram_layout_evaluator import TrigramLayoutEvaluator
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
from models.trigram_cost import TrigramCostWeights
from optimizer.vowel_seed_builder import VowelSeedBuilder


def make_layout() -> Layout:
    return Layout(
        name="Harmonia Seed Integration",
        version="5.1b",
        layer="L0",
        description="Seed builder integration test",
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
            allowed_positions=frozenset({
                "L-R-T-1",
                "L-M-T-2",
                "L-I-T-3",
                "L-I-T-4",
                "L-R-H-1",
                "L-M-H-2",
                "L-I-H-3",
                "L-I-H-4",
            }),
        ),
        forbidden_position=ForbiddenPositionConstraintConfig(
            enabled=False,
            forbidden_positions=frozenset(),
        ),
    )


def make_finger_load_budgets() -> tuple[FingerLoadBudget, ...]:
    return (
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            target_ratio=0.25,
            tolerance=0.05,
        ),
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.MIDDLE,
            target_ratio=0.15,
            tolerance=0.05,
        ),
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.RING,
            target_ratio=0.07,
            tolerance=0.03,
        ),
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.PINKY,
            target_ratio=0.03,
            tolerance=0.02,
        ),
        FingerLoadBudget(
            hand=Hand.RIGHT,
            finger=Finger.INDEX,
            target_ratio=0.25,
            tolerance=0.05,
        ),
        FingerLoadBudget(
            hand=Hand.RIGHT,
            finger=Finger.MIDDLE,
            target_ratio=0.15,
            tolerance=0.05,
        ),
        FingerLoadBudget(
            hand=Hand.RIGHT,
            finger=Finger.RING,
            target_ratio=0.07,
            tolerance=0.03,
        ),
        FingerLoadBudget(
            hand=Hand.RIGHT,
            finger=Finger.PINKY,
            target_ratio=0.03,
            tolerance=0.02,
        ),
    )


def make_evaluator() -> CandidateEvaluator:
    return CandidateEvaluator(
        constraint_set=ConstraintFactory.create(
            make_constraint_config()
        ),
        layout_evaluator=LayoutEvaluator(
            TransitionCostWeights(
                same_finger_penalty=10.0,
                same_hand_penalty=2.0,
                row_change_penalty=1.5,
                alternation_reward=2.0,
                inward_roll_reward=1.5,
                outward_roll_reward=0.5,
            )
        ),
        finger_load_pipeline=FingerLoadPipeline(),
        candidate_scorer=CandidateScorer(
            CandidateScoreWeights(
                transition_weight=1.0,
                finger_load_weight=1.0,
            )
        ),
        finger_load_budgets=(
            FingerLoadBudget(
                hand=Hand.LEFT,
                finger=Finger.INDEX,
                target_ratio=0.25,
                tolerance=0.05,
            ),
            FingerLoadBudget(
                hand=Hand.LEFT,
                finger=Finger.MIDDLE,
                target_ratio=0.15,
                tolerance=0.05,
            ),
            FingerLoadBudget(
                hand=Hand.LEFT,
                finger=Finger.RING,
                target_ratio=0.07,
                tolerance=0.03,
            ),
            FingerLoadBudget(
                hand=Hand.LEFT,
                finger=Finger.PINKY,
                target_ratio=0.03,
                tolerance=0.02,
            ),
            FingerLoadBudget(
                hand=Hand.RIGHT,
                finger=Finger.INDEX,
                target_ratio=0.25,
                tolerance=0.05,
            ),
            FingerLoadBudget(
                hand=Hand.RIGHT,
                finger=Finger.MIDDLE,
                target_ratio=0.15,
                tolerance=0.05,
            ),
            FingerLoadBudget(
                hand=Hand.RIGHT,
                finger=Finger.RING,
                target_ratio=0.07,
                tolerance=0.03,
            ),
            FingerLoadBudget(
                hand=Hand.RIGHT,
                finger=Finger.PINKY,
                target_ratio=0.03,
                tolerance=0.02,
            ),
        ),
    )


def make_fast_evaluator() -> FastCandidateEvaluator:
    transition_cost_weights = TransitionCostWeights(
        same_finger_penalty=10.0,
        same_hand_penalty=2.0,
        row_change_penalty=1.5,
        alternation_reward=2.0,
        inward_roll_reward=1.5,
        outward_roll_reward=0.5,
    )

    finger_load_budgets = (
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            target_ratio=0.25,
            tolerance=0.05,
        ),
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.MIDDLE,
            target_ratio=0.15,
            tolerance=0.05,
        ),
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.RING,
            target_ratio=0.07,
            tolerance=0.03,
        ),
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.PINKY,
            target_ratio=0.03,
            tolerance=0.02,
        ),
        FingerLoadBudget(
            hand=Hand.RIGHT,
            finger=Finger.INDEX,
            target_ratio=0.25,
            tolerance=0.05,
        ),
        FingerLoadBudget(
            hand=Hand.RIGHT,
            finger=Finger.MIDDLE,
            target_ratio=0.15,
            tolerance=0.05,
        ),
        FingerLoadBudget(
            hand=Hand.RIGHT,
            finger=Finger.RING,
            target_ratio=0.07,
            tolerance=0.03,
        ),
        FingerLoadBudget(
            hand=Hand.RIGHT,
            finger=Finger.PINKY,
            target_ratio=0.03,
            tolerance=0.02,
        ),
    )

    candidate_score_weights = CandidateScoreWeights(
        transition_weight=1.0,
        finger_load_weight=1.0,
    )

    return FastCandidateEvaluator(
        constraint_set=ConstraintFactory.create(
            make_constraint_config()
        ),
        layout_evaluator=FastLayoutScoreEvaluator(
            transition_cost_weights
        ),
        finger_load_evaluator=(
            FastFingerLoadScoreEvaluator(
                finger_load_budgets
            )
        ),
        candidate_scorer=FastCandidateScorer(
            candidate_score_weights
        ),
    )


def make_trigram_cost_weights() -> TrigramCostWeights:
    return TrigramCostWeights(
        same_finger_skip_penalty=8.0,
        redirect_penalty=4.0,
        alternation_reward=2.0,
        inward_roll_reward=1.5,
        outward_roll_reward=0.5,
    )


def make_trigram_evaluator() -> CandidateEvaluator:
    transition_cost_weights = TransitionCostWeights(
        same_finger_penalty=10.0,
        same_hand_penalty=2.0,
        row_change_penalty=1.5,
        alternation_reward=2.0,
        inward_roll_reward=1.5,
        outward_roll_reward=0.5,
    )

    return CandidateEvaluator(
        constraint_set=ConstraintFactory.create(
            make_constraint_config()
        ),
        layout_evaluator=LayoutEvaluator(
            transition_cost_weights
        ),
        finger_load_pipeline=FingerLoadPipeline(),
        candidate_scorer=CandidateScorer(
            CandidateScoreWeights(
                transition_weight=1.0,
                trigram_weight=1.0,
                finger_load_weight=1.0,
            )
        ),
        finger_load_budgets=make_finger_load_budgets(),
        trigram_layout_evaluator=TrigramLayoutEvaluator(
            make_trigram_cost_weights()
        ),
    )


def make_fast_trigram_evaluator() -> FastCandidateEvaluator:
    transition_cost_weights = TransitionCostWeights(
        same_finger_penalty=10.0,
        same_hand_penalty=2.0,
        row_change_penalty=1.5,
        alternation_reward=2.0,
        inward_roll_reward=1.5,
        outward_roll_reward=0.5,
    )

    return FastCandidateEvaluator(
        constraint_set=ConstraintFactory.create(
            make_constraint_config()
        ),
        layout_evaluator=FastLayoutScoreEvaluator(
            transition_cost_weights
        ),
        finger_load_evaluator=(
            FastFingerLoadScoreEvaluator(
                make_finger_load_budgets()
            )
        ),
        candidate_scorer=FastCandidateScorer(
            CandidateScoreWeights(
                transition_weight=1.0,
                trigram_weight=1.0,
                finger_load_weight=1.0,
            )
        ),
        trigram_layout_evaluator=(
            FastTrigramLayoutScoreEvaluator(
                make_trigram_cost_weights()
            )
        ),
    )


def make_statistics():
    corpus = Corpus(
        entries=(
            CorpusEntry(
                text=(
                    "THE QUICK BROWN FOX JUMPS "
                    "OVER THE LAZY DOG"
                )
            ),
        )
    )

    return (
        CorpusAnalyzer().analyze(corpus),
        CharacterAnalyzer().analyze(corpus),
    )


def test_build_returns_valid_left_vowel_seed():
    transition_statistics, character_statistics = (
        make_statistics()
    )

    config = make_constraint_config()

    builder = VowelSeedBuilder(
        evaluator=make_evaluator(),
        allowed_positions=(
            config.vowel_position.allowed_positions
        ),
    )

    result = builder.build(
        layout=make_layout(),
        transition_statistics=transition_statistics,
        character_statistics=character_statistics,
    )

    assert result.is_valid is True
    assert result.score is not None

    allowed = config.vowel_position.allowed_positions

    for vowel in "AEIOU":
        assert result.layout.position(vowel) in allowed


def test_build_moves_all_vowels_to_left_hand():
    transition_statistics, character_statistics = (
        make_statistics()
    )

    config = make_constraint_config()

    builder = VowelSeedBuilder(
        evaluator=make_evaluator(),
        allowed_positions=(
            config.vowel_position.allowed_positions
        ),
    )

    result = builder.build(
        layout=make_layout(),
        transition_statistics=transition_statistics,
        character_statistics=character_statistics,
    )

    for vowel in "AEIOU":
        assert result.layout.position(vowel).startswith(
            "L-"
        )


def test_fast_build_matches_normal_build():
    transition_statistics, character_statistics = (
        make_statistics()
    )

    config = make_constraint_config()
    layout = make_layout()

    normal_builder = VowelSeedBuilder(
        evaluator=make_evaluator(),
        allowed_positions=(
            config.vowel_position.allowed_positions
        ),
    )

    fast_builder = VowelSeedBuilder(
        evaluator=make_evaluator(),
        fast_evaluator=make_fast_evaluator(),
        allowed_positions=(
            config.vowel_position.allowed_positions
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

    assert fast_result.is_valid is True
    assert fast_result.score == normal_result.score

    for vowel in "AEIOU":
        assert (
            fast_result.layout.position(vowel)
            == normal_result.layout.position(vowel)
        )

    assert (
        fast_builder.evaluated_candidate_count
        == normal_builder.evaluated_candidate_count
    )

def test_fast_build_matches_normal_build_with_trigrams():
    corpus = Corpus(
        entries=(
            CorpusEntry(
                text=(
                    "THE QUICK BROWN FOX JUMPS "
                    "OVER THE LAZY DOG"
                )
            ),
        )
    )

    corpus_analyzer = CorpusAnalyzer()
    transition_statistics = corpus_analyzer.analyze(
        corpus
    )
    trigram_statistics = corpus_analyzer.analyze_trigrams(
        corpus
    )
    character_statistics = CharacterAnalyzer().analyze(
        corpus
    )

    config = make_constraint_config()
    layout = make_layout()

    normal_builder = VowelSeedBuilder(
        evaluator=make_trigram_evaluator(),
        allowed_positions=(
            config.vowel_position.allowed_positions
        ),
    )

    fast_builder = VowelSeedBuilder(
        evaluator=make_trigram_evaluator(),
        fast_evaluator=make_fast_trigram_evaluator(),
        allowed_positions=(
            config.vowel_position.allowed_positions
        ),
    )

    normal_result = normal_builder.build(
        layout=layout,
        transition_statistics=transition_statistics,
        character_statistics=character_statistics,
        trigram_statistics=trigram_statistics,
    )

    fast_result = fast_builder.build(
        layout=layout,
        transition_statistics=transition_statistics,
        character_statistics=character_statistics,
        trigram_statistics=trigram_statistics,
    )

    assert normal_result.is_valid is True
    assert fast_result.is_valid is True

    assert normal_result.score is not None
    assert fast_result.score is not None

    assert fast_result.score == normal_result.score

    for vowel in "AEIOU":
        assert (
            fast_result.layout.position(vowel)
            == normal_result.layout.position(vowel)
        )

    assert (
        fast_builder.evaluated_candidate_count
        == normal_builder.evaluated_candidate_count
    )
