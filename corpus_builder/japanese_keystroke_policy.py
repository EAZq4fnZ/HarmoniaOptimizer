from __future__ import annotations

from enum import Enum

from corpus_builder.japanese_corpus_part import (
    JapaneseCorpusPart,
    JapaneseCorpusPartKind,
)
from corpus_builder.japanese_keystroke_ambiguity import (
    JapaneseKeystrokeAmbiguityClass,
)
from corpus_builder.japanese_source_processing_relation import (
    JapaneseSourceProcessingRelation,
)


class JapaneseKeystrokePolicy(str, Enum):
    """How a Japanese source span contributes to the keystroke corpus."""

    ROMANIZE = "romanize"
    PRESERVE = "preserve"
    CANONICALIZE = "canonicalize"
    EXCLUDE = "exclude"
    AMBIGUOUS = "ambiguous"


def resolve_japanese_keystroke_policy(
    part: JapaneseCorpusPart,
) -> JapaneseKeystrokePolicy:
    """Resolve the Contract v1 policy for a structured corpus part."""
    if (
        part.kind
        is JapaneseCorpusPartKind.JAPANESE_LEXICAL
    ):
        return JapaneseKeystrokePolicy.ROMANIZE

    if (
        part.kind
        is JapaneseCorpusPartKind.ASCII_LITERAL
    ):
        return JapaneseKeystrokePolicy.PRESERVE

    if (
        part.kind
        is JapaneseCorpusPartKind.PUNCTUATION
    ):
        return JapaneseKeystrokePolicy.CANONICALIZE

    if (
        part.kind
        is JapaneseCorpusPartKind.HARMONIA_NATIVE
    ):
        return JapaneseKeystrokePolicy.PRESERVE

    if (
        part.kind
        is JapaneseCorpusPartKind.AMBIGUOUS
    ):
        return JapaneseKeystrokePolicy.AMBIGUOUS

    raise ValueError(
        "Unsupported Japanese corpus part kind: "
        f"{part.kind!r}"
    )


def resolve_ambiguous_japanese_keystroke_policy(
    *,
    ambiguity_class: JapaneseKeystrokeAmbiguityClass,
    relation: JapaneseSourceProcessingRelation,
) -> JapaneseKeystrokePolicy:
    """Resolve policy for an ambiguity audit observation.

    Contract v1 intentionally leaves all currently audited ambiguity
    classes unresolved. The relation describes what preprocessing did;
    it does not establish the user's original keystrokes.

    The arguments are retained explicitly so future contract revisions
    can add narrowly scoped policy decisions without changing this API.
    """
    del ambiguity_class
    del relation

    return JapaneseKeystrokePolicy.AMBIGUOUS
