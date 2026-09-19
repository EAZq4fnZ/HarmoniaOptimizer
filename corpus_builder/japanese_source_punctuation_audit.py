# corpus_builder/japanese_source_punctuation_audit.py

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

OPEN_TO_CLOSE = {
    "「": "」",
    "『": "』",
    "【": "】",
}

CLOSE_TO_OPEN = {
    close: open_
    for open_, close in OPEN_TO_CLOSE.items()
}


@dataclass(frozen=True, slots=True)
class JapaneseSourceBracketPairCount:
    open_symbol: str
    close_symbol: str
    source_open_count: int
    source_close_count: int
    matched_pair_count: int
    unmatched_open_count: int
    unmatched_close_count: int
    document_count: int


@dataclass(frozen=True, slots=True)
class JapaneseSourceBracketMismatchCount:
    close_symbol: str
    expected_open: str
    actual_stack_top: str
    count: int
    document_count: int


@dataclass(frozen=True, slots=True)
class JapaneseSourcePunctuationAuditResult:
    document_count: int
    documents_with_brackets: int
    pair_counts: tuple[
        JapaneseSourceBracketPairCount,
        ...,
    ]
    mismatch_counts: tuple[
        JapaneseSourceBracketMismatchCount,
        ...,
    ]
    mismatched_close_count: int
    documents_with_mismatch: int
    nested_matched_pair_count: int
    documents_with_nested_matched_pairs: int
    maximum_strict_stack_depth: int


@dataclass(frozen=True, slots=True)
class _OpenBracket:
    symbol: str
    depth: int


def audit_japanese_source_punctuation(
    texts: Iterable[str],
) -> JapaneseSourcePunctuationAuditResult:
    source_counts: Counter[str] = Counter()

    matched_pair_counts: Counter[
        tuple[str, str]
    ] = Counter()

    unmatched_open_counts: Counter[str] = Counter()
    unmatched_close_counts: Counter[str] = Counter()

    mismatch_counts: Counter[
        tuple[str, str, str]
    ] = Counter()

    pair_document_sets: defaultdict[
        tuple[str, str],
        set[int],
    ] = defaultdict(set)

    mismatch_document_sets: defaultdict[
        tuple[str, str, str],
        set[int],
    ] = defaultdict(set)

    documents_with_brackets: set[int] = set()
    documents_with_mismatch: set[int] = set()
    documents_with_nested_pairs: set[int] = set()

    nested_matched_pair_count = 0
    maximum_strict_stack_depth = 0
    document_count = 0

    target_symbols = frozenset(
        (*OPEN_TO_CLOSE, *CLOSE_TO_OPEN)
    )

    for document_index, text in enumerate(texts):
        document_count += 1

        stack: list[_OpenBracket] = []

        for symbol in text:
            if symbol in target_symbols:
                source_counts[symbol] += 1
                documents_with_brackets.add(
                    document_index
                )

            if symbol in OPEN_TO_CLOSE:
                depth = len(stack) + 1

                stack.append(
                    _OpenBracket(
                        symbol=symbol,
                        depth=depth,
                    )
                )

                maximum_strict_stack_depth = max(
                    maximum_strict_stack_depth,
                    depth,
                )

                continue

            if symbol not in CLOSE_TO_OPEN:
                continue

            expected_open = CLOSE_TO_OPEN[symbol]

            if not stack:
                unmatched_close_counts[symbol] += 1
                continue

            top = stack[-1]

            if top.symbol != expected_open:
                key = (
                    symbol,
                    expected_open,
                    top.symbol,
                )

                mismatch_counts[key] += 1
                mismatch_document_sets[key].add(
                    document_index
                )
                documents_with_mismatch.add(
                    document_index
                )

                # Strict typed-stack recovery:
                # a mismatched close does not mutate
                # the stack.
                continue

            stack.pop()

            pair_key = (
                top.symbol,
                symbol,
            )

            matched_pair_counts[pair_key] += 1
            pair_document_sets[pair_key].add(
                document_index
            )

            if top.depth > 1:
                nested_matched_pair_count += 1
                documents_with_nested_pairs.add(
                    document_index
                )

        for open_bracket in stack:
            unmatched_open_counts[
                open_bracket.symbol
            ] += 1

    pair_rows = tuple(
        JapaneseSourceBracketPairCount(
            open_symbol=open_symbol,
            close_symbol=close_symbol,
            source_open_count=source_counts[
                open_symbol
            ],
            source_close_count=source_counts[
                close_symbol
            ],
            matched_pair_count=matched_pair_counts[
                (
                    open_symbol,
                    close_symbol,
                )
            ],
            unmatched_open_count=(
                unmatched_open_counts[
                    open_symbol
                ]
            ),
            unmatched_close_count=(
                unmatched_close_counts[
                    close_symbol
                ]
            ),
            document_count=len(
                pair_document_sets[
                    (
                        open_symbol,
                        close_symbol,
                    )
                ]
            ),
        )
        for (
            open_symbol,
            close_symbol,
        ) in OPEN_TO_CLOSE.items()
    )

    mismatch_rows = tuple(
        JapaneseSourceBracketMismatchCount(
            close_symbol=close_symbol,
            expected_open=expected_open,
            actual_stack_top=actual_stack_top,
            count=mismatch_counts[
                (
                    close_symbol,
                    expected_open,
                    actual_stack_top,
                )
            ],
            document_count=len(
                mismatch_document_sets[
                    (
                        close_symbol,
                        expected_open,
                        actual_stack_top,
                    )
                ]
            ),
        )
        for (
            close_symbol,
            expected_open,
            actual_stack_top,
        ) in sorted(mismatch_counts)
    )

    return JapaneseSourcePunctuationAuditResult(
        document_count=document_count,
        documents_with_brackets=len(
            documents_with_brackets
        ),
        pair_counts=pair_rows,
        mismatch_counts=mismatch_rows,
        mismatched_close_count=sum(
            mismatch_counts.values()
        ),
        documents_with_mismatch=len(
            documents_with_mismatch
        ),
        nested_matched_pair_count=(
            nested_matched_pair_count
        ),
        documents_with_nested_matched_pairs=len(
            documents_with_nested_pairs
        ),
        maximum_strict_stack_depth=(
            maximum_strict_stack_depth
        ),
    )