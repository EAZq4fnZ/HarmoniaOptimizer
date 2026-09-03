from __future__ import annotations

import argparse
from collections.abc import Callable
from pathlib import Path
from typing import Any

from corpus_builder.japanese_audit import (
    audit_japanese_texts,
)
from corpus_builder.japanese_romanizer import (
    romanize_japanese_reading,
)
from corpus_builder.sudachi_reader import (
    SudachiTokenizer,
)


def _make_default_tokenizer() -> SudachiTokenizer:
    from sudachipy import Dictionary, SplitMode

    return Dictionary(
        dict="core"
    ).create(
        mode=SplitMode.C
    )


def audit_file(
    path: Path,
    *,
    auditor: Callable[[object], Any],
) -> Any:
    with path.open(
        "r",
        encoding="utf-8",
    ) as source:
        return auditor(source)


def audit_default_file(
    path: Path,
    *,
    tokenizer_factory: Callable[
        [],
        SudachiTokenizer,
    ] = _make_default_tokenizer,
    romanizer: Callable[
        [str],
        str,
    ] = romanize_japanese_reading,
    audit_texts: Callable[..., Any] = audit_japanese_texts,
) -> Any:
    tokenizer = tokenizer_factory()

    def auditor(
        texts: object,
    ) -> Any:
        return audit_texts(
            texts,
            tokenizer=tokenizer,
            romanizer=romanizer,
        )

    return audit_file(
        path,
        auditor=auditor,
    )



def main(
    argv: list[str] | None = None,
) -> int:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "source",
        type=Path,
    )

    args = parser.parse_args(argv)

    result = audit_default_file(
        args.source
    )

    print(
        f"total_morphemes: "
        f"{result.total_morphemes}"
    )
    print(
        f"successful_morphemes: "
        f"{result.successful_morphemes}"
    )
    print(
        f"failed_morphemes: "
        f"{result.failed_morphemes}"
    )
    print(
        f"issues: "
        f"{len(result.issues)}"
    )

    for issue in sorted(
        result.issues,
        key=lambda issue: issue.count,
        reverse=True,
    ):
        print(
            f"surface: "
            f"{issue.surface}"
        )
        print(
            f"reading: "
            f"{issue.reading}"
        )
        print(
            f"part_of_speech: "
            f"{issue.part_of_speech}"
        )
        print(
            f"count: "
            f"{issue.count}"
        )
        print(
            f"context: "
            f"{issue.context}"
        )
        print(
            f"error: "
            f"{issue.error}"
        )

    return 0



if __name__ == "__main__":
    raise SystemExit(
        main()
    )
