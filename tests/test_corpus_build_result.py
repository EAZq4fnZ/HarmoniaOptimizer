import pytest

from corpus_builder.corpus_build_result import (
    CorpusBuildResult,
)
from corpus_builder.corpus_mix import CorpusMix
from evaluator.character_analyzer import CharacterAnalyzer


def test_corpus_build_result_records_processed_text_metrics() -> None:
    result = CorpusBuildResult(
        category="japanese",
        text="abcABC xyz",
        source_document_count=10_000,
    )

    assert result.category == "japanese"
    assert result.text == "abcABC xyz"
    assert result.source_document_count == 10_000
    assert result.ascii_letter_count == 9


def test_corpus_build_result_rejects_empty_category() -> None:
    with pytest.raises(
        ValueError,
        match="category must not be empty",
    ):
        CorpusBuildResult(
            category="",
            text="abc",
            source_document_count=1,
        )


def test_corpus_build_result_rejects_empty_text() -> None:
    with pytest.raises(
        ValueError,
        match="text must not be empty",
    ):
        CorpusBuildResult(
            category="japanese",
            text="",
            source_document_count=1,
        )


@pytest.mark.parametrize(
    "source_document_count",
    (
        0,
        -1,
    ),
)
def test_corpus_build_result_rejects_non_positive_document_count(
    source_document_count: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="source_document_count must be greater than 0",
    ):
        CorpusBuildResult(
            category="japanese",
            text="abc",
            source_document_count=source_document_count,
        )


def test_corpus_build_result_rejects_text_without_ascii_letters() -> None:
    with pytest.raises(
        ValueError,
        match="text must contain at least one ASCII letter",
    ):
        CorpusBuildResult(
            category="japanese",
            text="123!?",
            source_document_count=1,
        )

def test_corpus_build_result_converts_to_corpus_mix_source() -> None:
    result = CorpusBuildResult(
        category="japanese",
        text="abcABC",
        source_document_count=10,
    )

    source = result.to_mix_source(
        target_ratio=0.5,
    )

    assert source.text == "abcABC"
    assert source.target_ratio == pytest.approx(
        0.5
    )

def test_corpus_build_results_preserve_target_ratios_through_mix() -> None:
    japanese = CorpusBuildResult(
        category="japanese",
        text="A" * 200,
        source_document_count=100,
    )
    english = CorpusBuildResult(
        category="english",
        text="B" * 100,
        source_document_count=50,
    )

    mix = CorpusMix(
        sources=(
            japanese.to_mix_source(
                target_ratio=0.6,
            ),
            english.to_mix_source(
                target_ratio=0.4,
            ),
        )
    )

    statistics = CharacterAnalyzer().analyze(
        mix.build()
    )

    assert statistics.weighted_count(
        "a"
    ) == pytest.approx(0.6)

    assert statistics.weighted_count(
        "b"
    ) == pytest.approx(0.4)

    assert statistics.total_weighted() == pytest.approx(
        1.0
    )
