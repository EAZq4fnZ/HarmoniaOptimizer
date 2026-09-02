import pytest

from corpus_builder.corpus_mix import (
    CorpusMix,
    CorpusMixSource,
)
from evaluator.character_analyzer import CharacterAnalyzer


def test_corpus_mix_normalizes_target_ratios_by_ascii_letter_count() -> None:
    mix = CorpusMix(
        sources=(
            CorpusMixSource(
                text="A" * 100,
                target_ratio=0.5,
            ),
            CorpusMixSource(
                text="B" * 50,
                target_ratio=0.5,
            ),
        )
    )

    corpus = mix.build()

    assert corpus.entries[0].weight == pytest.approx(
        0.5 / 100
    )
    assert corpus.entries[1].weight == pytest.approx(
        0.5 / 50
    )

    statistics = CharacterAnalyzer().analyze(corpus)

    assert statistics.weighted_count(
        "a"
    ) == pytest.approx(0.5)
    assert statistics.weighted_count(
        "b"
    ) == pytest.approx(0.5)

    assert statistics.total_weighted() == pytest.approx(
        1.0
    )


def test_corpus_mix_rejects_source_without_ascii_letters() -> None:
    mix = CorpusMix(
        sources=(
            CorpusMixSource(
                text="1234!?[]{}",
                target_ratio=1.0,
            ),
        )
    )

    with pytest.raises(
        ValueError,
        match="Corpus mix source must contain at least one ASCII letter",
    ):
        mix.build()


@pytest.mark.parametrize(
    "target_ratio",
    (
        0.0,
        -0.1,
    ),
)
def test_corpus_mix_rejects_non_positive_target_ratio(
    target_ratio: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="target_ratio must be greater than 0",
    ):
        CorpusMixSource(
            text="abc",
            target_ratio=target_ratio,
        )


def test_corpus_mix_rejects_target_ratios_not_summing_to_one() -> None:
    with pytest.raises(
        ValueError,
        match="target ratios must sum to 1.0",
    ):
        CorpusMix(
            sources=(
                CorpusMixSource(
                    text="abc",
                    target_ratio=0.5,
                ),
                CorpusMixSource(
                    text="def",
                    target_ratio=0.4,
                ),
            )
        )


def test_corpus_mix_rejects_empty_sources() -> None:
    with pytest.raises(
        ValueError,
        match="Corpus mix must contain at least one source",
    ):
        CorpusMix(
            sources=()
        )
