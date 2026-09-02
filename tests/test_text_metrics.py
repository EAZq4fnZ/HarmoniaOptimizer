from corpus_builder.text_metrics import (
    count_ascii_letters,
)


def test_count_ascii_letters_counts_only_ascii_a_to_z() -> None:
    assert count_ascii_letters(
        "AbC xyz 123 あいう !? é"
    ) == 6
