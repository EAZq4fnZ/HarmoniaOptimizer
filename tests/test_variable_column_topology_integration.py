from __future__ import annotations

import string

import pytest

from evaluator.candidate_evaluator import CandidateEvaluator
from evaluator.candidate_scorer import CandidateScorer
from evaluator.character_statistics import CharacterStatistics
from evaluator.constraint_set import ConstraintSet
from evaluator.fast_candidate_evaluator import FastCandidateEvaluator
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
from evaluator.fast_trigram_layout_score_evaluator import (
    FastTrigramLayoutScoreEvaluator,
)
from evaluator.finger_load_pipeline import FingerLoadPipeline
from evaluator.forbidden_position_constraint import (
    ForbiddenPositionConstraint,
)
from evaluator.key_position_evaluator import KeyPositionEvaluator
from evaluator.layout_evaluator import LayoutEvaluator
from evaluator.transition_statistics import TransitionStatistics
from evaluator.trigram_layout_evaluator import TrigramLayoutEvaluator
from evaluator.trigram_statistics import TrigramStatistics
from evaluator.vowel_position_constraint import VowelPositionConstraint
from models.candidate_score import CandidateScoreWeights
from models.enums import Finger, Hand
from models.finger_load_budget import FingerLoadBudget
from models.key_position_cost import KeyPositionCostProfile
from models.layout import Layout
from models.transition_cost import TransitionCostWeights
from models.trigram_cost import TrigramCostWeights
from optimizer.local_search_optimizer import LocalSearchOptimizer
from optimizer.random_start_layout_factory import RandomStartLayoutFactory
from optimizer.swap_candidate_generator import SwapCandidateGenerator


def make_3x6_topology() -> tuple[str, ...]:
    """
    Return a test-only 3x6 split logical-position topology.

    This fixture exists only to prove that Core semantics do not
    require the topology position count to equal the A-Z optimization
    target count.

    3 rows x 6 columns x 2 hands = 36 positions.

    The sixth column is intentionally represented with the existing
    canonical LogicalPosition format. No new topology-specific parser
    or Core branch is introduced.
    """

    finger_by_column = (
        "P",
        "R",
        "M",
        "I",
        "I",
        "I",
    )

    positions: list[str] = []

    for hand in ("L", "R"):
        for row in ("T", "H", "B"):
            for column, finger in enumerate(
                finger_by_column
            ):
                positions.append(
                    f"{hand}-{finger}-{row}-{column}"
                )

    return tuple(positions)


def make_layout(
    topology: tuple[str, ...],
) -> Layout:
    """
    Map the current A-Z optimization domain onto only 26 of the
    36 available topology positions.
    """

    active_positions = topology[:26]

    return Layout(
        name="GT1 Test-Only 3x6 Layout",
        version="0.1.0",
        layer="L0",
        description=(
            "Variable-column topology architecture proof fixture"
        ),
        mapping=dict(
            zip(
                string.ascii_uppercase,
                active_positions,
                strict=True,
            )
        ),
    )


def make_transition_statistics() -> TransitionStatistics:
    statistics = TransitionStatistics()

    statistics.add(
        {
            ("A", "B"): 17,
            ("B", "A"): 11,
            ("A", "E"): 23,
            ("E", "I"): 19,
            ("I", "O"): 13,
            ("O", "U"): 7,
            ("T", "H"): 29,
            ("H", "E"): 31,
            ("R", "E"): 5,
        }
    )

    return statistics


def make_character_statistics() -> CharacterStatistics:
    statistics = CharacterStatistics()

    statistics.add(
        {
            "A": 80,
            "B": 12,
            "E": 70,
            "H": 25,
            "I": 60,
            "O": 50,
            "R": 20,
            "T": 30,
            "U": 40,
        }
    )

    return statistics


def make_trigram_statistics() -> TrigramStatistics:
    statistics = TrigramStatistics()

    statistics.record(
        "A",
        "B",
        "A",
        weight=13.0,
    )
    statistics.record(
        "A",
        "E",
        "I",
        weight=17.0,
    )
    statistics.record(
        "T",
        "H",
        "E",
        weight=19.0,
    )
    statistics.record(
        "I",
        "O",
        "U",
        weight=11.0,
    )

    return statistics


def make_transition_weights() -> TransitionCostWeights:
    return TransitionCostWeights(
        same_finger_penalty=10.0,
        same_hand_penalty=2.0,
        row_change_penalty=1.5,
        alternation_reward=2.0,
        inward_roll_reward=1.5,
        outward_roll_reward=0.5,
    )


def make_trigram_weights() -> TrigramCostWeights:
    return TrigramCostWeights(
        same_finger_skip_penalty=8.0,
        redirect_penalty=4.0,
        alternation_reward=2.0,
        inward_roll_reward=1.5,
        outward_roll_reward=0.5,
    )


def make_candidate_weights() -> CandidateScoreWeights:
    return CandidateScoreWeights(
        transition_weight=1.25,
        trigram_weight=0.75,
        finger_load_weight=1.5,
        position_weight=2.0,
    )


def make_fast_candidate_weights() -> CandidateScoreWeights:
    """
    FastCandidateEvaluator's compatibility path currently evaluates
    transition and finger load only.

    Trigram and position parity are tested separately through their
    existing prepared fast paths.
    """

    return CandidateScoreWeights(
        transition_weight=1.25,
        trigram_weight=0.0,
        finger_load_weight=1.5,
        position_weight=0.0,
    )


def make_finger_load_budgets() -> tuple[
    FingerLoadBudget,
    ...
]:
    return (
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.PINKY,
            target_ratio=0.15,
            tolerance=0.05,
        ),
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.RING,
            target_ratio=0.15,
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
            finger=Finger.INDEX,
            target_ratio=0.25,
            tolerance=0.05,
        ),
        FingerLoadBudget(
            hand=Hand.RIGHT,
            finger=Finger.PINKY,
            target_ratio=0.15,
            tolerance=0.05,
        ),
        FingerLoadBudget(
            hand=Hand.RIGHT,
            finger=Finger.RING,
            target_ratio=0.15,
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
            finger=Finger.INDEX,
            target_ratio=0.25,
            tolerance=0.05,
        ),
    )


def make_position_profile(
    topology: tuple[str, ...],
) -> KeyPositionCostProfile:
    """
    Test-only synthetic costs.

    These values are not an ergonomic 3x6 product profile.
    They merely ensure that all 36 topology positions participate
    in a valid arbitrary-position cost space.
    """

    return KeyPositionCostProfile(
        costs={
            position: index / 100.0
            for index, position in enumerate(topology)
        }
    )


def make_constraints(
    layout: Layout,
    topology: tuple[str, ...],
) -> ConstraintSet:
    vowels = frozenset(
        layout.position(vowel)
        for vowel in ("A", "E", "I", "O", "U")
    )

    unused_positions = (
        frozenset(topology)
        - frozenset(layout.positions())
    )

    return ConstraintSet(
        [
            VowelPositionConstraint(vowels),
            ForbiddenPositionConstraint(
                unused_positions
            ),
        ]
    )


def make_normal_evaluator(
    constraints: ConstraintSet,
    topology: tuple[str, ...],
    *,
    weights: CandidateScoreWeights | None = None,
) -> CandidateEvaluator:
    return CandidateEvaluator(
        constraint_set=constraints,
        layout_evaluator=LayoutEvaluator(
            make_transition_weights()
        ),
        finger_load_pipeline=FingerLoadPipeline(),
        candidate_scorer=CandidateScorer(
            weights or make_candidate_weights()
        ),
        finger_load_budgets=make_finger_load_budgets(),
        trigram_layout_evaluator=TrigramLayoutEvaluator(
            make_trigram_weights()
        ),
        key_position_evaluator=KeyPositionEvaluator(
            make_position_profile(topology)
        ),
    )


def make_fast_evaluator(
    constraints: ConstraintSet,
) -> FastCandidateEvaluator:
    return FastCandidateEvaluator(
        constraint_set=constraints,
        layout_evaluator=FastLayoutScoreEvaluator(
            make_transition_weights()
        ),
        finger_load_evaluator=FastFingerLoadScoreEvaluator(
            make_finger_load_budgets()
        ),
        candidate_scorer=FastCandidateScorer(
            make_fast_candidate_weights()
        ),
    )


def make_letter_position_indexes(
    layout: Layout,
    position_indexes: dict[str, int],
) -> list[int]:
    return [
        position_indexes[
            layout.position(letter)
        ]
        for letter in string.ascii_uppercase
    ]


def test_gt1_separates_topology_count_from_symbol_count() -> None:
    topology = make_3x6_topology()
    layout = make_layout(topology)

    assert len(topology) == 36
    assert len(set(topology)) == 36

    assert len(layout) == 26
    assert set(layout.mapping) == set(
        string.ascii_uppercase
    )

    used_positions = set(layout.positions())
    unused_positions = (
        set(topology)
        - used_positions
    )

    assert len(used_positions) == 26
    assert len(unused_positions) == 10

    assert used_positions <= set(topology)


def test_gt1_constraints_accept_26_of_36_positions() -> None:
    topology = make_3x6_topology()
    layout = make_layout(topology)

    constraints = make_constraints(
        layout,
        topology,
    )

    result = constraints.evaluate(layout)

    assert result.is_valid


def test_gt1_candidate_generation_and_random_start_preserve_domain() -> None:
    topology = make_3x6_topology()
    layout = make_layout(topology)

    candidates = (
        SwapCandidateGenerator()
        .generate_candidates(layout)
    )

    assert len(candidates) == 325

    expected_positions = set(
        layout.positions()
    )

    for candidate in candidates:
        assert len(candidate.layout) == 26
        assert (
            set(candidate.layout.positions())
            == expected_positions
        )

    random_layout = (
        RandomStartLayoutFactory(seed=20260920)
        .create(
            base_layout=layout,
            run_index=0,
        )
    )

    assert len(random_layout) == 26
    assert (
        set(random_layout.positions())
        == expected_positions
    )


def test_gt1_normal_evaluation_supports_3x6_position_space() -> None:
    topology = make_3x6_topology()
    layout = make_layout(topology)

    constraints = make_constraints(
        layout,
        topology,
    )

    evaluator = make_normal_evaluator(
        constraints,
        topology,
    )

    result = evaluator.evaluate(
        layout=layout,
        transition_statistics=make_transition_statistics(),
        character_statistics=make_character_statistics(),
        trigram_statistics=make_trigram_statistics(),
    )

    assert result.is_valid
    assert result.layout_evaluation is not None
    assert result.candidate_score is not None
    assert result.score is not None

    candidate_score = result.candidate_score

    assert (
        candidate_score.transition_score
        == pytest.approx(
            result.layout_evaluation.total_cost
            / result.layout_evaluation.evaluated_weight
        )
    )

    assert candidate_score.trigram_score != 0.0
    assert candidate_score.position_score >= 0.0
    assert candidate_score.finger_load_score >= 0.0

    assert result.score == pytest.approx(
        candidate_score.weighted_transition_score
        + candidate_score.weighted_trigram_score
        + candidate_score.weighted_finger_load_score
        + candidate_score.weighted_position_score
    )


def test_gt1_fast_candidate_matches_normal_compatibility_semantics() -> None:
    topology = make_3x6_topology()
    layout = make_layout(topology)

    constraints = make_constraints(
        layout,
        topology,
    )

    compatibility_weights = (
        make_fast_candidate_weights()
    )

    normal = make_normal_evaluator(
        constraints,
        topology,
        weights=compatibility_weights,
    )

    fast = make_fast_evaluator(
        constraints,
    )

    transitions = make_transition_statistics()
    characters = make_character_statistics()

    normal_result = normal.evaluate(
        layout=layout,
        transition_statistics=transitions,
        character_statistics=characters,
    )

    fast_score = fast.evaluate(
        layout=layout,
        transition_statistics=transitions,
        character_statistics=characters,
    )

    assert normal_result.score is not None
    assert fast_score is not None

    assert fast_score == pytest.approx(
        normal_result.score
    )


def test_gt1_fast_position_index_uses_all_36_positions() -> None:
    topology = make_3x6_topology()
    layout = make_layout(topology)

    fast = make_fast_evaluator(
        make_constraints(
            layout,
            topology,
        )
    )

    (
        position_indexes,
        cost_matrix,
        position_finger_indexes,
        allowed_ratios,
    ) = fast.prepare_position_index(
        topology
    )

    assert len(position_indexes) == 36
    assert len(cost_matrix) == 36
    assert all(
        len(row) == 36
        for row in cost_matrix
    )

    assert len(position_finger_indexes) == 36
    assert len(allowed_ratios) > 0

    integer_positions = (
        make_letter_position_indexes(
            layout,
            position_indexes,
        )
    )

    assert len(integer_positions) == 26
    assert len(set(integer_positions)) == 26
    assert all(
        0 <= position < 36
        for position in integer_positions
    )


def test_gt1_fast_four_component_score_matches_detailed_evaluation() -> None:
    topology = make_3x6_topology()
    layout = make_layout(topology)

    transitions = make_transition_statistics()
    characters = make_character_statistics()
    trigrams = make_trigram_statistics()

    constraints = make_constraints(
        layout,
        topology,
    )

    candidate_weights = make_candidate_weights()
    transition_weights = make_transition_weights()
    trigram_weights = make_trigram_weights()
    position_profile = make_position_profile(
        topology
    )

    normal = make_normal_evaluator(
        constraints,
        topology,
        weights=candidate_weights,
    )

    normal_result = normal.evaluate(
        layout=layout,
        transition_statistics=transitions,
        character_statistics=characters,
        trigram_statistics=trigrams,
    )

    assert normal_result.score is not None

    fast_layout = FastLayoutScoreEvaluator(
        transition_weights
    )
    fast_finger = FastFingerLoadScoreEvaluator(
        make_finger_load_budgets()
    )
    fast_trigram = FastTrigramLayoutScoreEvaluator(
        trigram_weights
    )
    fast_position = FastKeyPositionScoreEvaluator(
        position_profile
    )
    fast_scorer = FastCandidateScorer(
        candidate_weights
    )

    (
        position_indexes,
        cost_matrix,
    ) = fast_layout.build_position_index(
        topology
    )

    integer_positions = (
        make_letter_position_indexes(
            layout,
            position_indexes,
        )
    )

    fast_layout_score = (
        fast_layout.evaluate_position_indexed(
            integer_positions,
            cost_matrix,
            transitions,
        )
    )

    (
        position_finger_indexes,
        allowed_ratios,
    ) = fast_finger.build_position_finger_index(
        topology,
        position_indexes,
    )

    fast_finger_score = (
        fast_finger.evaluate_position_indexed(
            integer_positions,
            position_finger_indexes,
            allowed_ratios,
            characters,
        )
    )

    trigram_cube = (
        fast_trigram.build_cost_cube(
            topology
        )
    )

    prepared_trigrams = (
        fast_trigram.prepare_position_indexed_trigrams(
            trigrams
        )
    )

    fast_trigram_score = (
        fast_trigram
        .evaluate_prepared_position_indexed_complete(
            integer_positions,
            trigram_cube,
            prepared_trigrams,
        )
    )

    position_costs = (
        fast_position.build_position_costs(
            topology
        )
    )

    (
        weighted_statistics,
        total_weighted_load,
    ) = (
        fast_position
        .prepare_position_indexed_statistics(
            characters
        )
    )

    fast_position_score = (
        fast_position
        .evaluate_prepared_position_indexed_complete(
            integer_positions,
            position_costs,
            weighted_statistics,
            total_weighted_load,
        )
    )

    fast_total = fast_scorer.score(
        transition_total_cost=(
            fast_layout_score.total_cost
        ),
        evaluated_transition_weight=(
            fast_layout_score.evaluated_weight
        ),
        finger_load_penalty=fast_finger_score,
        trigram_total_cost=(
            fast_trigram_score.total_cost
        ),
        evaluated_trigram_weight=(
            fast_trigram_score.evaluated_weight
        ),
        position_score=fast_position_score,
    )

    assert fast_total == pytest.approx(
        normal_result.score
    )


def test_gt1_local_search_runs_without_topology_specific_branch() -> None:
    topology = make_3x6_topology()
    layout = make_layout(topology)

    evaluator = make_normal_evaluator(
        ConstraintSet([]),
        topology,
    )

    optimizer = LocalSearchOptimizer(
        candidate_evaluator=evaluator,
        max_iterations=1,
    )

    result = optimizer.optimize(
        layout=layout,
        transition_statistics=make_transition_statistics(),
        character_statistics=make_character_statistics(),
        trigram_statistics=make_trigram_statistics(),
    )

    assert result.initial_evaluation.is_valid
    assert result.initial_evaluation.score is not None

    assert result.final_evaluation.is_valid
    assert result.final_evaluation.score is not None

    assert len(result.final_evaluation.layout) == 26

    assert (
        set(result.final_evaluation.layout.positions())
        == set(layout.positions())
    )
