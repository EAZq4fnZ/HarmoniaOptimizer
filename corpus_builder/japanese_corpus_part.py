from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class JapaneseCorpusPartKind(str, Enum):
    JAPANESE_LEXICAL = "japanese_lexical"
    ASCII_LITERAL = "ascii_literal"
    PUNCTUATION = "punctuation"
    HARMONIA_NATIVE = "harmonia_native"
    AMBIGUOUS = "ambiguous"


@dataclass(frozen=True, slots=True)
class JapaneseCorpusPart:
    kind: JapaneseCorpusPartKind
    source_text: str
    processing_text: str
