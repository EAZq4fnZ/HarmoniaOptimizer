# tests/test_swap_candidate_generator.py

from models.layout import Layout
from optimizer.swap_candidate_generator import (
    SwapCandidateGenerator,
)


def make_layout() -> Layout:
    return Layout(
        name="Candidate Generator Test",
        version="0.1.0",
        layer="L0",
        description="Swap candidate generator test",
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


def mapping_signature(
    layout: Layout,
) -> tuple[tuple[str, str], ...]:
    """
    Return a hashable representation of a layout mapping.
    """

    return tuple(sorted(layout.mapping.items()))


def test_generate_returns_tuple():
    generator = SwapCandidateGenerator()

    candidates = generator.generate(
        make_layout()
    )

    assert isinstance(candidates, tuple)


def test_generate_creates_325_candidates():
    generator = SwapCandidateGenerator()

    candidates = generator.generate(
        make_layout()
    )

    assert len(candidates) == 325


def test_all_candidates_are_layouts():
    generator = SwapCandidateGenerator()

    candidates = generator.generate(
        make_layout()
    )

    assert all(
        isinstance(candidate, Layout)
        for candidate in candidates
    )


def test_all_candidates_are_unique():
    generator = SwapCandidateGenerator()

    candidates = generator.generate(
        make_layout()
    )

    signatures = {
        mapping_signature(candidate)
        for candidate in candidates
    }

    assert len(signatures) == 325


def test_original_layout_is_not_included():
    layout = make_layout()
    generator = SwapCandidateGenerator()

    candidates = generator.generate(layout)

    original_signature = mapping_signature(layout)

    candidate_signatures = {
        mapping_signature(candidate)
        for candidate in candidates
    }

    assert original_signature not in candidate_signatures


def test_first_candidate_swaps_a_and_b():
    layout = make_layout()
    generator = SwapCandidateGenerator()

    candidates = generator.generate(layout)

    first = candidates[0]

    assert first.position("A") == layout.position("B")
    assert first.position("B") == layout.position("A")


def test_first_candidate_preserves_other_letters():
    layout = make_layout()
    generator = SwapCandidateGenerator()

    candidates = generator.generate(layout)

    first = candidates[0]

    for letter in layout.letters():
        if letter not in {"A", "B"}:
            assert first.position(letter) == layout.position(letter)


def test_last_candidate_swaps_y_and_z():
    layout = make_layout()
    generator = SwapCandidateGenerator()

    candidates = generator.generate(layout)

    last = candidates[-1]

    assert last.position("Y") == layout.position("Z")
    assert last.position("Z") == layout.position("Y")


def test_generation_does_not_modify_original_layout():
    layout = make_layout()
    original_signature = mapping_signature(layout)

    generator = SwapCandidateGenerator()

    generator.generate(layout)

    assert mapping_signature(layout) == original_signature


def test_candidate_metadata_is_preserved():
    layout = make_layout()
    generator = SwapCandidateGenerator()

    candidates = generator.generate(layout)

    candidate = candidates[0]

    assert candidate.name == layout.name
    assert candidate.version == layout.version
    assert candidate.layer == layout.layer
    assert candidate.description == layout.description


def test_generate_candidates_returns_325_candidates():
    layout = make_layout()
    generator = SwapCandidateGenerator()

    candidates = generator.generate_candidates(layout)

    assert len(candidates) == 325


def test_generate_candidates_preserves_swap_move():
    layout = make_layout()
    generator = SwapCandidateGenerator()

    candidates = generator.generate_candidates(layout)

    first = candidates[0]

    assert first.move.first_letter == "A"
    assert first.move.second_letter == "B"


def test_generate_candidates_preserves_swapped_layout():
    layout = make_layout()
    generator = SwapCandidateGenerator()

    candidates = generator.generate_candidates(layout)

    first = candidates[0]

    assert first.layout.position("A") == layout.position("B")
    assert first.layout.position("B") == layout.position("A")


def test_generate_matches_candidate_layouts():
    layout = make_layout()
    generator = SwapCandidateGenerator()

    layouts = generator.generate(layout)
    candidates = generator.generate_candidates(layout)

    assert layouts == tuple(
        candidate.layout
        for candidate in candidates
    )


def test_last_generated_candidate_preserves_y_z_move():
    layout = make_layout()
    generator = SwapCandidateGenerator()

    candidates = generator.generate_candidates(layout)

    last = candidates[-1]

    assert last.move.first_letter == "Y"
    assert last.move.second_letter == "Z"