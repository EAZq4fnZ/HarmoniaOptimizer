# tests/test_fast_candidate_evaluator.py

from __future__ import annotations

import pytest

from evaluator.candidate_evaluator import CandidateEvaluator
from evaluator.candidate_scorer import CandidateScorer
from evaluator.character_statistics import CharacterStatistics
from evaluator.constraint_set import ConstraintSet
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
from evaluator.forbidden_position_constraint import (
    ForbiddenPositionConstraint,
)
from evaluator.layout_evaluator import LayoutEvaluator
from evaluator.transition_statistics import TransitionStatistics
from evaluator.trigram_layout_evaluator import TrigramLayoutEvaluator
from evaluator.trigram_statistics import TrigramStatistics
from models.candidate_score import CandidateScoreWeights
from models.enums import Finger, Hand
from models.finger_load_budget import FingerLoadBudget
from models.layout import Layout
from models.transition_cost import TransitionCostWeights
from models.trigram_cost import TrigramCostWeights


def make_layout() -> Layout:
    return Layout(
        name="Fast Candidate Test Layout",
        version="0.1.0",
        layer="L0",
        description="Fast candidate evaluator test layout",
        mapping={
            "A": "L-I-H-3",
            "B": "R-I-H-3",
            "C": "L-R-H-1",
            "D": "L-M-T-2",
            "E": "L-M-H-2",
            "F": "L-I-T-3",
            "G": "L-I-H-4",
            "H": "L-I-T-4",
            "I": "R-I-T-3",
            "J": "R-I-H-4",
            "K": "R-I-T-4",
            "L": "R-M-H-2",
            "M": "R-R-H-1",
            "N": "R-M-T-2",
            "O": "R-M-B-2",
            "P": "R-R-T-1",
            "Q": "L-P-H-0",
            "R": "L-R-T-1",
            "S": "L-M-B-2",
            "T": "L-I-B-3",
            "U": "R-R-B-1",
            "V": "R-I-B-3",
            "W": "R-P-H-0",
            "X": "L-P-T-0",
            "Y": "L-P-B-0",
            "Z": "R-P-T-0",
        },
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


def make_candidate_weights() -> CandidateScoreWeights:
    return CandidateScoreWeights(
        transition_weight=1.0,
        finger_load_weight=1.0,
    )


def make_trigram_weights() -> TrigramCostWeights:
    return TrigramCostWeights(
        same_finger_skip_penalty=8.0,
        redirect_penalty=4.0,
        alternation_reward=2.0,
        inward_roll_reward=1.5,
        outward_roll_reward=0.5,
    )


def make_trigram_statistics() -> TrigramStatistics:
    statistics = TrigramStatistics()

    statistics.record(
        "A",
        "B",
        "A",
        weight=10.0,
    )
    statistics.record(
        "A",
        "E",
        "I",
        weight=7.0,
    )
    statistics.record(
        "E",
        "A",
        "U",
        weight=5.0,
    )
    statistics.record(
        "I",
        "J",
        "I",
        weight=3.0,
    )

    return statistics


def make_transition_statistics() -> TransitionStatistics:
    statistics = TransitionStatistics()

    statistics.add(
        {
            ("A", "B"): 10,
            ("B", "A"): 7,
            ("A", "E"): 12,
            ("A", "F"): 5,
            ("E", "A"): 9,
            ("I", "J"): 6,
        }
    )

    return statistics


def make_character_statistics() -> CharacterStatistics:
    statistics = CharacterStatistics()

    statistics.add(
        {
            "A": 70,
            "B": 30,
            "E": 40,
            "I": 20,
            "J": 10,
        }
    )

    return statistics


def make_finger_load_budgets() -> tuple[
    FingerLoadBudget,
    ...
]:
    return (
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.INDEX,
            target_ratio=0.30,
            tolerance=0.05,
        ),
        FingerLoadBudget(
            hand=Hand.LEFT,
            finger=Finger.MIDDLE,
            target_ratio=0.20,
            tolerance=0.05,
        ),
        FingerLoadBudget(
            hand=Hand.RIGHT,
            finger=Finger.INDEX,
            target_ratio=0.30,
            tolerance=0.05,
        ),
        FingerLoadBudget(
            hand=Hand.RIGHT,
            finger=Finger.MIDDLE,
            target_ratio=0.20,
            tolerance=0.05,
        ),
    )


def make_normal_evaluator(
    constraint_set: ConstraintSet,
) -> CandidateEvaluator:
    return CandidateEvaluator(
        constraint_set=constraint_set,
        layout_evaluator=LayoutEvaluator(
            make_transition_weights()
        ),
        finger_load_pipeline=FingerLoadPipeline(),
        candidate_scorer=CandidateScorer(
            make_candidate_weights()
        ),
        finger_load_budgets=make_finger_load_budgets(),
    )


def make_fast_evaluator(
    constraint_set: ConstraintSet,
) -> FastCandidateEvaluator:
    return FastCandidateEvaluator(
        constraint_set=constraint_set,
        layout_evaluator=FastLayoutScoreEvaluator(
            make_transition_weights()
        ),
        finger_load_evaluator=FastFingerLoadScoreEvaluator(
            make_finger_load_budgets()
        ),
        candidate_scorer=FastCandidateScorer(
            make_candidate_weights()
        ),
    )


def test_fast_candidate_matches_normal_candidate() -> None:
    layout = make_layout()
    transitions = make_transition_statistics()
    characters = make_character_statistics()

    normal = make_normal_evaluator(
        ConstraintSet([])
    )

    fast = make_fast_evaluator(
        ConstraintSet([])
    )

    normal_result = normal.evaluate(
        layout,
        transitions,
        characters,
    )

    fast_score = fast.evaluate(
        layout,
        transitions,
        characters,
    )

    assert normal_result.score is not None
    assert fast_score is not None

    assert fast_score == pytest.approx(
        normal_result.score
    )


def test_fast_candidate_matches_after_layout_change() -> None:
    first_layout = make_layout()

    changed_mapping = dict(
        first_layout.mapping
    )

    changed_mapping["A"], changed_mapping["B"] = (
        changed_mapping["B"],
        changed_mapping["A"],
    )

    second_layout = Layout(
        name="Fast Candidate Swapped Layout",
        version=first_layout.version,
        layer=first_layout.layer,
        description=first_layout.description,
        mapping=changed_mapping,
    )

    transitions = make_transition_statistics()
    characters = make_character_statistics()

    normal = make_normal_evaluator(
        ConstraintSet([])
    )

    fast = make_fast_evaluator(
        ConstraintSet([])
    )

    normal_result = normal.evaluate(
        second_layout,
        transitions,
        characters,
    )

    fast_score = fast.evaluate(
        second_layout,
        transitions,
        characters,
    )

    assert normal_result.score is not None
    assert fast_score is not None

    assert fast_score == pytest.approx(
        normal_result.score
    )


def test_fast_candidate_rejects_invalid_layout() -> None:
    constraint = ForbiddenPositionConstraint(
        frozenset({
            "L-I-H-3",
        })
    )

    fast = make_fast_evaluator(
        ConstraintSet([constraint])
    )

    result = fast.evaluate(
        make_layout(),
        make_transition_statistics(),
        make_character_statistics(),
    )

    assert result is None


def test_fast_candidate_handles_empty_statistics() -> None:
    layout = make_layout()

    normal = make_normal_evaluator(
        ConstraintSet([])
    )

    fast = make_fast_evaluator(
        ConstraintSet([])
    )

    transitions = TransitionStatistics()
    characters = CharacterStatistics()

    normal_result = normal.evaluate(
        layout,
        transitions,
        characters,
    )

    fast_score = fast.evaluate(
        layout,
        transitions,
        characters,
    )

    assert normal_result.score is not None
    assert fast_score is not None

    assert fast_score == pytest.approx(
        normal_result.score
    )


def test_fast_candidate_can_be_reused() -> None:
    fast = make_fast_evaluator(
        ConstraintSet([])
    )

    normal = make_normal_evaluator(
        ConstraintSet([])
    )

    first_layout = make_layout()

    changed_mapping = dict(
        first_layout.mapping
    )

    changed_mapping["A"], changed_mapping["E"] = (
        changed_mapping["E"],
        changed_mapping["A"],
    )

    second_layout = Layout(
        name="Fast Candidate Reuse Layout",
        version=first_layout.version,
        layer=first_layout.layer,
        description=first_layout.description,
        mapping=changed_mapping,
    )

    transitions = make_transition_statistics()
    characters = make_character_statistics()

    for layout in (
        first_layout,
        second_layout,
    ):
        normal_result = normal.evaluate(
            layout,
            transitions,
            characters,
        )

        fast_score = fast.evaluate(
            layout,
            transitions,
            characters,
        )

        assert normal_result.score is not None
        assert fast_score is not None

        assert fast_score == pytest.approx(
            normal_result.score
        )


def test_evaluate_mapping_matches_evaluate() -> None:
    layout = make_layout()
    transitions = make_transition_statistics()
    characters = make_character_statistics()

    fast = make_fast_evaluator(
        ConstraintSet([])
    )

    layout_score = fast.evaluate(
        layout,
        transitions,
        characters,
    )

    mapping_score = fast.evaluate_mapping(
        layout.mapping,
        transitions,
        characters,
    )

    assert layout_score is not None

    assert mapping_score == pytest.approx(
        layout_score
    )


def test_evaluate_mapping_matches_after_layout_change() -> None:
    first_layout = make_layout()

    changed_mapping = dict(
        first_layout.mapping
    )

    changed_mapping["A"], changed_mapping["E"] = (
        changed_mapping["E"],
        changed_mapping["A"],
    )

    second_layout = Layout(
        name="Fast Candidate Mapping Test Layout",
        version=first_layout.version,
        layer=first_layout.layer,
        description=first_layout.description,
        mapping=changed_mapping,
    )

    transitions = make_transition_statistics()
    characters = make_character_statistics()

    fast = make_fast_evaluator(
        ConstraintSet([])
    )

    layout_score = fast.evaluate(
        second_layout,
        transitions,
        characters,
    )

    mapping_score = fast.evaluate_mapping(
        changed_mapping,
        transitions,
        characters,
    )

    assert layout_score is not None

    assert mapping_score == pytest.approx(
        layout_score
    )


def test_evaluate_mapping_handles_empty_statistics() -> None:
    layout = make_layout()

    fast = make_fast_evaluator(
        ConstraintSet([])
    )

    layout_score = fast.evaluate(
        layout,
        TransitionStatistics(),
        CharacterStatistics(),
    )

    mapping_score = fast.evaluate_mapping(
        layout.mapping,
        TransitionStatistics(),
        CharacterStatistics(),
    )

    assert layout_score is not None

    assert mapping_score == pytest.approx(
        layout_score
    )


def evaluate_indexed(
    self,
    positions: list[str | None],
    mapping: dict[str, str],
    transition_statistics: TransitionStatistics,
    character_statistics: CharacterStatistics,
) -> float:
    layout_score = self._layout_evaluator.evaluate_indexed(
        positions,
        transition_statistics,
    )

    finger_load_penalty = (
        self._finger_load_evaluator.evaluate_mapping(
            mapping,
            character_statistics,
        )
    )

    return self._candidate_scorer.score(
        transition_total_cost=layout_score.total_cost,
        evaluated_transition_weight=(
            layout_score.evaluated_weight
        ),
        finger_load_penalty=finger_load_penalty,
    )


def test_evaluate_indexed_matches_mapping() -> None:
    layout = make_layout()
    transitions = make_transition_statistics()
    characters = make_character_statistics()

    fast = make_fast_evaluator(
        ConstraintSet([])
    )

    positions: list[str | None] = [
        None
    ] * 26

    for letter, position in layout.mapping.items():
        index = (
            ord(letter.upper())
            - ord("A")
        )

        if 0 <= index < 26:
            positions[index] = position

    mapping_score = fast.evaluate_mapping(
        layout.mapping,
        transitions,
        characters,
    )

    indexed_score = fast.evaluate_indexed(
        positions,
        transitions,
        characters,
    )

    assert indexed_score == pytest.approx(
        mapping_score
    )


def test_evaluate_position_indexed_matches_mapping() -> None:
    layout = make_layout()
    transitions = make_transition_statistics()
    characters = make_character_statistics()

    fast = make_fast_evaluator(
        ConstraintSet([])
    )

    string_positions: list[str | None] = [
        None
    ] * 26

    for letter, position in layout.mapping.items():
        index = (
            ord(letter.upper())
            - ord("A")
        )

        if 0 <= index < 26:
            string_positions[index] = position

    logical_positions = tuple(
        position
        for position in string_positions
        if position is not None
    )

    (
        position_indexes,
        cost_matrix,
    ) = fast._layout_evaluator.build_position_index(
        logical_positions
    )

    integer_positions = (
        fast._layout_evaluator.convert_to_position_indexes(
            string_positions,
            position_indexes,
        )
    )

    (
        position_finger_indexes,
        allowed_ratios,
    ) = (
        fast
        ._finger_load_evaluator
        .build_position_finger_index(
            logical_positions,
            position_indexes,
        )
    )

    mapping_score = fast.evaluate_mapping(
        layout.mapping,
        transitions,
        characters,
    )

    indexed_score = fast.evaluate_position_indexed(
        list(integer_positions),
        cost_matrix,
        position_finger_indexes,
        allowed_ratios,
        transitions,
        characters,
    )

    assert indexed_score == pytest.approx(
        mapping_score
    )


def test_evaluate_position_indexed_flat_matches_mapping() -> None:
    layout = make_layout()
    transitions = make_transition_statistics()
    characters = make_character_statistics()

    fast = make_fast_evaluator(
        ConstraintSet([])
    )

    string_positions: list[str | None] = [
        None
    ] * 26

    for letter, position in layout.mapping.items():
        index = (
            ord(letter.upper())
            - ord("A")
        )

        if 0 <= index < 26:
            string_positions[index] = position

    logical_positions = tuple(
        position
        for position in string_positions
        if position is not None
    )

    (
        position_indexes,
        flat_costs,
        position_count,
        position_finger_indexes,
        allowed_ratios,
    ) = fast.prepare_flat_position_index(
        logical_positions
    )

    integer_positions = tuple(
        -1
        if position is None
        else position_indexes[position]
        for position in string_positions
    )

    mapping_score = fast.evaluate_mapping(
        layout.mapping,
        transitions,
        characters,
    )

    flat_score = (
        fast.evaluate_position_indexed_flat(
            list(integer_positions),
            flat_costs,
            position_count,
            position_finger_indexes,
            allowed_ratios,
            transitions,
            characters,
        )
    )

    assert flat_score == pytest.approx(
        mapping_score
    )


def test_evaluate_prepared_position_indexed_matches_mapping() -> None:
    layout = make_layout()
    transitions = make_transition_statistics()
    characters = make_character_statistics()

    fast = make_fast_evaluator(
        ConstraintSet([])
    )

    string_positions: list[str | None] = [
        None
    ] * 26

    for letter, position in layout.mapping.items():
        index = (
            ord(letter.upper())
            - ord("A")
        )

        if 0 <= index < 26:
            string_positions[index] = position

    logical_positions = tuple(
        position
        for position in string_positions
        if position is not None
    )

    (
        position_indexes,
        cost_matrix,
        position_finger_indexes,
        allowed_ratios,
    ) = fast.prepare_position_index(
        logical_positions
    )

    integer_positions = [
        (
            -1
            if position is None
            else position_indexes[position]
        )
        for position in string_positions
    ]

    prepared_transitions = (
        fast.prepare_position_indexed_transitions(
            transitions
        )
    )

    mapping_score = fast.evaluate_mapping(
        layout.mapping,
        transitions,
        characters,
    )

    position_indexed_score = (
        fast.evaluate_position_indexed(
            integer_positions,
            cost_matrix,
            position_finger_indexes,
            allowed_ratios,
            transitions,
            characters,
        )
    )

    prepared_score = (
        fast.evaluate_prepared_position_indexed(
            integer_positions,
            cost_matrix,
            prepared_transitions,
            position_finger_indexes,
            allowed_ratios,
            characters,
        )
    )

    assert prepared_score == pytest.approx(
        mapping_score
    )

    assert prepared_score == pytest.approx(
        position_indexed_score
    )

def test_evaluate_prepared_position_indexed_delta_matches_prepared() -> None:
    layout = make_layout()
    transitions = make_transition_statistics()
    characters = make_character_statistics()

    fast = make_fast_evaluator(
        ConstraintSet([])
    )

    string_positions: list[str | None] = [
        None
    ] * 26

    for letter, position in layout.mapping.items():
        index = (
            ord(letter.upper())
            - ord("A")
        )

        if 0 <= index < 26:
            string_positions[index] = position

    logical_positions = tuple(
        position
        for position in string_positions
        if position is not None
    )

    (
        position_indexes,
        cost_matrix,
        position_finger_indexes,
        allowed_ratios,
    ) = fast.prepare_position_index(
        logical_positions
    )

    base_positions = list(
        fast._layout_evaluator
        .convert_to_position_indexes(
            string_positions,
            position_indexes,
        )
    )

    prepared_transitions = (
        fast.prepare_position_indexed_transitions(
            transitions
        )
    )

    transition_baseline = (
        fast.prepare_prepared_position_indexed_delta(
            base_positions,
            cost_matrix,
            prepared_transitions,
        )
    )

    candidate_positions = list(
        base_positions
    )

    a_index = ord("A") - ord("A")
    e_index = ord("E") - ord("A")

    (
        candidate_positions[a_index],
        candidate_positions[e_index],
    ) = (
        candidate_positions[e_index],
        candidate_positions[a_index],
    )

    prepared_score = (
        fast.evaluate_prepared_position_indexed(
            candidate_positions,
            cost_matrix,
            prepared_transitions,
            position_finger_indexes,
            allowed_ratios,
            characters,
        )
    )

    delta_score = (
        fast.evaluate_prepared_position_indexed_delta(
            candidate_positions,
            cost_matrix,
            transition_baseline,
            (
                a_index,
                e_index,
            ),
            position_finger_indexes,
            allowed_ratios,
            characters,
        )
    )

    assert delta_score == pytest.approx(
        prepared_score
    )

def test_fully_prepared_fast_candidate_matches_normal_with_trigrams() -> None:
    layout = make_layout()
    transitions = make_transition_statistics()
    trigrams = make_trigram_statistics()
    characters = make_character_statistics()

    candidate_weights = CandidateScoreWeights(
        transition_weight=1.7,
        trigram_weight=2.3,
        finger_load_weight=0.8,
    )

    normal = CandidateEvaluator(
        constraint_set=ConstraintSet([]),
        layout_evaluator=LayoutEvaluator(
            make_transition_weights()
        ),
        finger_load_pipeline=FingerLoadPipeline(),
        candidate_scorer=CandidateScorer(
            candidate_weights
        ),
        finger_load_budgets=make_finger_load_budgets(),
        trigram_layout_evaluator=TrigramLayoutEvaluator(
            make_trigram_weights()
        ),
    )

    fast = FastCandidateEvaluator(
        constraint_set=ConstraintSet([]),
        layout_evaluator=FastLayoutScoreEvaluator(
            make_transition_weights()
        ),
        finger_load_evaluator=FastFingerLoadScoreEvaluator(
            make_finger_load_budgets()
        ),
        candidate_scorer=FastCandidateScorer(
            candidate_weights
        ),
        trigram_layout_evaluator=(
            FastTrigramLayoutScoreEvaluator(
                make_trigram_weights()
            )
        ),
    )

    normal_result = normal.evaluate(
        layout,
        transitions,
        characters,
        trigram_statistics=trigrams,
    )

    string_positions: list[str | None] = [
        None
    ] * 26

    for letter, position in layout.mapping.items():
        letter_index = (
            ord(letter.upper())
            - ord("A")
        )

        if 0 <= letter_index < 26:
            string_positions[letter_index] = position

    logical_positions = tuple(
        position
        for position in string_positions
        if position is not None
    )

    (
        position_indexes,
        cost_matrix,
        position_finger_indexes,
        allowed_ratios,
    ) = fast.prepare_position_index(
        logical_positions
    )

    integer_positions = [
        (
            -1
            if position is None
            else position_indexes[position]
        )
        for position in string_positions
    ]

    prepared_transitions = (
        fast.prepare_position_indexed_transitions(
            transitions
        )
    )

    weighted_statistics, total_weighted_load = (
        fast.prepare_position_indexed_character_statistics(
            characters
        )
    )

    trigram_cost_cube = fast.build_trigram_cost_cube(
        logical_positions
    )

    prepared_trigrams = (
        fast.prepare_position_indexed_trigrams(
            trigrams
        )
    )

    fast_score = (
        fast.evaluate_fully_prepared_position_indexed_complete(
            integer_positions,
            cost_matrix,
            prepared_transitions,
            position_finger_indexes,
            allowed_ratios,
            weighted_statistics,
            total_weighted_load,
            trigram_cost_cube=trigram_cost_cube,
            prepared_trigrams=prepared_trigrams,
        )
    )

    assert normal_result.score is not None

    assert fast_score == pytest.approx(
        normal_result.score
    )


def test_vowel_group_fast_candidate_matches_generic_fast_with_trigrams() -> None:
    layout = make_layout()
    transitions = make_transition_statistics()
    trigrams = make_trigram_statistics()
    characters = make_character_statistics()

    candidate_weights = CandidateScoreWeights(
        transition_weight=1.7,
        trigram_weight=2.3,
        finger_load_weight=0.8,
    )

    fast = FastCandidateEvaluator(
        constraint_set=ConstraintSet([]),
        layout_evaluator=FastLayoutScoreEvaluator(
            make_transition_weights()
        ),
        finger_load_evaluator=FastFingerLoadScoreEvaluator(
            make_finger_load_budgets()
        ),
        candidate_scorer=FastCandidateScorer(
            candidate_weights
        ),
        trigram_layout_evaluator=(
            FastTrigramLayoutScoreEvaluator(
                make_trigram_weights()
            )
        ),
    )

    string_positions: list[str | None] = [
        None
    ] * 26

    for letter, position in layout.mapping.items():
        letter_index = (
            ord(letter.upper())
            - ord("A")
        )

        if 0 <= letter_index < 26:
            string_positions[letter_index] = position

    logical_positions = tuple(
        position
        for position in string_positions
        if position is not None
    )

    (
        position_indexes,
        cost_matrix,
        position_finger_indexes,
        allowed_ratios,
    ) = fast.prepare_position_index(
        logical_positions
    )

    base_positions = [
        (
            -1
            if position is None
            else position_indexes[position]
        )
        for position in string_positions
    ]

    prepared_transitions = (
        fast.prepare_position_indexed_transitions(
            transitions
        )
    )

    weighted_statistics, total_weighted_load = (
        fast.prepare_position_indexed_character_statistics(
            characters
        )
    )

    trigram_cost_cube = fast.build_trigram_cost_cube(
        logical_positions
    )

    prepared_trigrams = (
        fast.prepare_position_indexed_trigrams(
            trigrams
        )
    )

    generic_score = (
        fast.evaluate_fully_prepared_position_indexed_complete(
            base_positions,
            cost_matrix,
            prepared_transitions,
            position_finger_indexes,
            allowed_ratios,
            weighted_statistics,
            total_weighted_load,
            trigram_cost_cube=trigram_cost_cube,
            prepared_trigrams=prepared_trigrams,
        )
    )

    selected_positions = (
        base_positions[0],
        base_positions[4],
        base_positions[8],
        base_positions[14],
        base_positions[20],
    )

    transition_group_costs = (
        fast.prepare_position_indexed_complete_vowel_group_transition_costs(
            base_positions,
            selected_positions,
            cost_matrix,
            prepared_transitions,
        )
    )

    finger_load_baseline = (
        fast.prepare_position_indexed_complete_vowel_group_finger_load_baseline(
            base_positions,
            position_finger_indexes,
            weighted_statistics,
            total_weighted_load,
        )
    )

    trigram_group_costs = (
        fast.prepare_position_indexed_complete_vowel_group_trigram_costs(
            base_positions,
            trigram_cost_cube,
            prepared_trigrams,
        )
    )

    (
        _layout_evaluator,
        _finger_load_evaluator,
        _trigram_evaluator,
        _transition_factor,
        trigram_factor,
        _finger_load_weight,
    ) = fast.prepare_complete_vowel_group_scalar_hot_path(
        prepared_transitions,
        prepared_trigrams,
    )

    group_score = (
        fast.evaluate_fully_prepared_position_indexed_complete_vowel_group(
            base_positions,
            cost_matrix,
            prepared_transitions,
            transition_group_costs,
            position_finger_indexes,
            allowed_ratios,
            weighted_statistics,
            finger_load_baseline,
            trigram_cost_cube=trigram_cost_cube,
            trigram_group_costs=trigram_group_costs,
            trigram_factor=trigram_factor,
        )
    )

    assert group_score == pytest.approx(
        generic_score
    )
