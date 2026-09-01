from __future__ import annotations

import hashlib
from pathlib import Path

from file_digest import sha256_file


def test_sha256_file(
    tmp_path: Path,
) -> None:
    path = tmp_path / "corpus.txt"

    content = "Harmonia 日本語 corpus"
    path.write_text(
        content,
        encoding="utf-8",
    )

    expected = hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()

    assert sha256_file(path) == expected
