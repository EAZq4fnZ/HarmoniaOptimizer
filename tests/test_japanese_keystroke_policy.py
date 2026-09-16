import pytest

from corpus_builder.japanese_corpus_part import (
    JapaneseCorpusPart,
    JapaneseCorpusPartKind,
)
from corpus_builder.japanese_keystroke_ambiguity import (
    JapaneseKeystrokeAmbiguityClass,
)
from corpus_builder.japanese_keystroke_context import (
    JapaneseKeystrokeContextEvidence,
)
from corpus_builder.japanese_keystroke_policy import (
    JapaneseKeystrokePolicy,
    resolve_ambiguous_japanese_keystroke_policy,
    resolve_contextual_japanese_keystroke_policy,
    resolve_japanese_keystroke_policy,
)
from corpus_builder.japanese_source_processing_relation import (
    JapaneseSourceProcessingRelation,
)


@pytest.mark.parametrize(
    (
        "kind",
        "source_text",
        "processing_text",
        "expected",
    ),
    [
        (
            JapaneseCorpusPartKind.JAPANESE_LEXICAL,
            "日本",
            "ニホン",
            JapaneseKeystrokePolicy.ROMANIZE,
        ),
        (
            JapaneseCorpusPartKind.ASCII_LITERAL,
            "Python",
            "Python",
            JapaneseKeystrokePolicy.PRESERVE,
        ),
        (
            JapaneseCorpusPartKind.PUNCTUATION,
            "！",
            "！",
            JapaneseKeystrokePolicy.CANONICALIZE,
        ),
        (
            JapaneseCorpusPartKind.HARMONIA_NATIVE,
            "、",
            "、",
            JapaneseKeystrokePolicy.PRESERVE,
        ),
        (
            JapaneseCorpusPartKind.AMBIGUOUS,
            "α",
            "アルファー",
            JapaneseKeystrokePolicy.AMBIGUOUS,
        ),
    ],
)
def test_resolve_japanese_keystroke_policy(
    kind: JapaneseCorpusPartKind,
    source_text: str,
    processing_text: str,
    expected: JapaneseKeystrokePolicy,
) -> None:
    part = JapaneseCorpusPart(
        kind=kind,
        source_text=source_text,
        processing_text=processing_text,
    )

    assert (
        resolve_japanese_keystroke_policy(
            part
        )
        is expected
    )


@pytest.mark.parametrize(
    "ambiguity_class",
    list(JapaneseKeystrokeAmbiguityClass),
)
@pytest.mark.parametrize(
    "relation",
    list(JapaneseSourceProcessingRelation),
)
def test_contract_v1_keeps_audited_ambiguities_ambiguous(
    ambiguity_class: JapaneseKeystrokeAmbiguityClass,
    relation: JapaneseSourceProcessingRelation,
) -> None:
    assert (
        resolve_ambiguous_japanese_keystroke_policy(
            ambiguity_class=ambiguity_class,
            relation=relation,
        )
        is JapaneseKeystrokePolicy.AMBIGUOUS
    )


def test_canonicalized_relation_does_not_resolve_ambiguous_span(
) -> None:
    assert (
        resolve_ambiguous_japanese_keystroke_policy(
            ambiguity_class=(
                JapaneseKeystrokeAmbiguityClass.OTHER
            ),
            relation=(
                JapaneseSourceProcessingRelation
                .CANONICALIZED
            ),
        )
        is JapaneseKeystrokePolicy.AMBIGUOUS
    )


def test_linguistic_reading_does_not_imply_romanize(
) -> None:
    assert (
        resolve_ambiguous_japanese_keystroke_policy(
            ambiguity_class=(
                JapaneseKeystrokeAmbiguityClass
                .SEMANTIC_SYMBOL
            ),
            relation=(
                JapaneseSourceProcessingRelation
                .LINGUISTIC_READING
            ),
        )
        is JapaneseKeystrokePolicy.AMBIGUOUS
    )


def test_lossy_relation_does_not_resolve_typographic_input(
) -> None:
    assert (
        resolve_ambiguous_japanese_keystroke_policy(
            ambiguity_class=(
                JapaneseKeystrokeAmbiguityClass
                .TYPOGRAPHIC
            ),
            relation=(
                JapaneseSourceProcessingRelation
                .LOSSY
            ),
        )
        is JapaneseKeystrokePolicy.AMBIGUOUS
    )


@pytest.mark.parametrize(
    "ambiguity_class",
    list(JapaneseKeystrokeAmbiguityClass),
)
@pytest.mark.parametrize(
    "relation",
    list(JapaneseSourceProcessingRelation),
)
def test_structural_kaomoji_context_excludes_ambiguity(
    ambiguity_class: JapaneseKeystrokeAmbiguityClass,
    relation: JapaneseSourceProcessingRelation,
) -> None:
    assert (
        resolve_contextual_japanese_keystroke_policy(
            ambiguity_class=ambiguity_class,
            relation=relation,
            context_evidence=(
                JapaneseKeystrokeContextEvidence
                .KAOMOJI_STRUCTURAL
            ),
        )
        is JapaneseKeystrokePolicy.EXCLUDE
    )


@pytest.mark.parametrize(
    "context_evidence",
    (
        JapaneseKeystrokeContextEvidence.NONE,
        JapaneseKeystrokeContextEvidence.DECORATIVE_ADJACENT,
    ),
)
@pytest.mark.parametrize(
    "ambiguity_class",
    list(JapaneseKeystrokeAmbiguityClass),
)
@pytest.mark.parametrize(
    "relation",
    list(JapaneseSourceProcessingRelation),
)
def test_non_structural_context_keeps_ambiguity_unresolved(
    context_evidence: JapaneseKeystrokeContextEvidence,
    ambiguity_class: JapaneseKeystrokeAmbiguityClass,
    relation: JapaneseSourceProcessingRelation,
) -> None:
    assert (
        resolve_contextual_japanese_keystroke_policy(
            ambiguity_class=ambiguity_class,
            relation=relation,
            context_evidence=context_evidence,
        )
        is JapaneseKeystrokePolicy.AMBIGUOUS
    )
