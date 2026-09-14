import pytest

from corpus_builder.japanese_corpus_part import (
    JapaneseCorpusPart,
    JapaneseCorpusPartKind,
)
from corpus_builder.japanese_keystroke_canonicalizer import (
    canonicalize_japanese_keystroke_text,
)
from corpus_builder.japanese_keystroke_policy import (
    JapaneseKeystrokePolicy,
    resolve_japanese_keystroke_policy,
)
from corpus_builder.japanese_preprocessor import (
    preprocess_japanese_corpus_part,
)
from corpus_builder.japanese_romanizer import (
    romanize_japanese_reading,
)


@pytest.mark.parametrize(
    (
        "part",
        "expected_policy",
        "expected_output",
    ),
    [
        (
            JapaneseCorpusPart(
                kind=(
                    JapaneseCorpusPartKind
                    .JAPANESE_LEXICAL
                ),
                source_text="日本",
                processing_text="ニホン",
            ),
            JapaneseKeystrokePolicy.ROMANIZE,
            "nihonn",
        ),
        (
            JapaneseCorpusPart(
                kind=(
                    JapaneseCorpusPartKind
                    .ASCII_LITERAL
                ),
                source_text="Python",
                processing_text="Python",
            ),
            JapaneseKeystrokePolicy.PRESERVE,
            "Python",
        ),
        (
            JapaneseCorpusPart(
                kind=(
                    JapaneseCorpusPartKind
                    .PUNCTUATION
                ),
                source_text="！",
                processing_text="！",
            ),
            JapaneseKeystrokePolicy.CANONICALIZE,
            "!",
        ),
        (
            JapaneseCorpusPart(
                kind=(
                    JapaneseCorpusPartKind
                    .HARMONIA_NATIVE
                ),
                source_text="、",
                processing_text="、",
            ),
            JapaneseKeystrokePolicy.PRESERVE,
            "、",
        ),
    ],
)
def test_structured_preprocessor_matches_policy_model(
    part: JapaneseCorpusPart,
    expected_policy: JapaneseKeystrokePolicy,
    expected_output: str,
) -> None:
    assert (
        resolve_japanese_keystroke_policy(
            part
        )
        is expected_policy
    )

    assert (
        preprocess_japanese_corpus_part(
            part,
            romanizer=romanize_japanese_reading,
            canonicalizer=(
                canonicalize_japanese_keystroke_text
            ),
        )
        == expected_output
    )


def test_ambiguous_policy_matches_preprocessor_rejection(
) -> None:
    part = JapaneseCorpusPart(
        kind=JapaneseCorpusPartKind.AMBIGUOUS,
        source_text="α",
        processing_text="アルファー",
    )

    assert (
        resolve_japanese_keystroke_policy(
            part
        )
        is JapaneseKeystrokePolicy.AMBIGUOUS
    )

    with pytest.raises(ValueError):
        preprocess_japanese_corpus_part(
            part,
            romanizer=romanize_japanese_reading,
            canonicalizer=(
                canonicalize_japanese_keystroke_text
            ),
        )
