# tests/test_main.py

from __future__ import annotations

import json
from pathlib import Path

import pytest

from main import (
    build_parser,
    main,
    run,
)


def make_layout_file(
    tmp_path: Path,
) -> Path:
    path = tmp_path / "layout.json"

    mapping = {
        "A": "L-I-H-3",
        "B": "R-I-H-3",
        "C": "L-R-H-1",
        "D": "L-M-T-2",
        "E": "L-M-H-2",
        "F": "L-I-T-3",
        "G": "L-I-H-4",
        "H": "L-I-T-4",
        "I": "R-I-T-3",
        "J": "R-I-H-4",
        "K": "R-I-T-4",
        "L": "R-M-H-2",
        "M": "R-R-H-1",
        "N": "R-M-T-2",
        "O": "R-M-B-2",
        "P": "R-R-T-1",
        "Q": "L-P-H-0",
        "R": "L-R-T-1",
        "S": "L-M-B-2",
        "T": "L-I-B-3",
        "U": "R-R-B-1",
        "V": "R-I-B-3",
        "W": "R-P-H-0",
        "X": "L-P-T-0",
        "Y": "L-P-B-0",
        "Z": "R-P-T-0",
    }

    data = {
        "name": "CLI Test",
        "version": "0.1.0",
        "layer": "L0",
        "description": "CLI test layout",
        "layout": mapping,
    }

    path.write_text(
        json.dumps(data),
        encoding="utf-8",
    )

    return path


def make_corpus_file(
    tmp_path: Path,
) -> Path:
    path = tmp_path / "corpus.txt"

    path.write_text(
        "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG",
        encoding="utf-8",
    )

    return path


def test_build_parser():
    parser = build_parser()

    args = parser.parse_args(
        [
            "layout.json",
            "corpus.txt",
        ]
    )

    assert args.layout == Path(
        "layout.json"
    )

    assert args.corpus == Path(
        "corpus.txt"
    )

    assert args.max_iterations == 10


def test_build_parser_accepts_max_iterations():
    parser = build_parser()

    args = parser.parse_args(
        [
            "layout.json",
            "corpus.txt",
            "--max-iterations",
            "3",
        ]
    )

    assert args.max_iterations == 3


def test_run_returns_report(
    tmp_path: Path,
):
    layout_path = make_layout_file(
        tmp_path
    )

    corpus_path = make_corpus_file(
        tmp_path
    )

    report = run(
        layout_path=layout_path,
        corpus_path=corpus_path,
        max_iterations=0,
    )

    assert isinstance(
        report,
        str,
    )

    assert "Optimization Result" in report
    assert "Initial score:" in report
    assert "Final score:" in report


def test_run_with_one_iteration(
    tmp_path: Path,
):
    layout_path = make_layout_file(
        tmp_path
    )

    corpus_path = make_corpus_file(
        tmp_path
    )

    report = run(
        layout_path=layout_path,
        corpus_path=corpus_path,
        max_iterations=1,
    )

    assert "Optimization Result" in report
    assert "Iterations:" in report


def test_run_rejects_empty_corpus(
    tmp_path: Path,
):
    layout_path = make_layout_file(
        tmp_path
    )

    corpus_path = (
        tmp_path
        / "empty.txt"
    )

    corpus_path.write_text(
        "",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="corpus file must not be empty",
    ):
        run(
            layout_path=layout_path,
            corpus_path=corpus_path,
            max_iterations=0,
        )


def test_run_rejects_negative_iterations(
    tmp_path: Path,
):
    layout_path = make_layout_file(
        tmp_path
    )

    corpus_path = make_corpus_file(
        tmp_path
    )

    with pytest.raises(
        ValueError,
        match="max_iterations",
    ):
        run(
            layout_path=layout_path,
            corpus_path=corpus_path,
            max_iterations=-1,
        )


def test_main_prints_report(
    tmp_path: Path,
    capsys,
):
    layout_path = make_layout_file(
        tmp_path
    )

    corpus_path = make_corpus_file(
        tmp_path
    )

    exit_code = main(
        [
            str(layout_path),
            str(corpus_path),
            "--max-iterations",
            "0",
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0

    assert (
        "Optimization Result"
        in captured.out
    )

    assert (
        "Initial score:"
        in captured.out
    )


def test_main_missing_layout_exits(
    tmp_path: Path,
):
    corpus_path = make_corpus_file(
        tmp_path
    )

    missing_layout = (
        tmp_path
        / "missing.json"
    )

    with pytest.raises(
        SystemExit,
    ) as exc_info:
        main(
            [
                str(missing_layout),
                str(corpus_path),
                "--max-iterations",
                "0",
            ]
        )

    assert exc_info.value.code == 2


def test_main_empty_corpus_exits(
    tmp_path: Path,
):
    layout_path = make_layout_file(
        tmp_path
    )

    corpus_path = (
        tmp_path
        / "empty.txt"
    )

    corpus_path.write_text(
        "",
        encoding="utf-8",
    )

    with pytest.raises(
        SystemExit,
    ) as exc_info:
        main(
            [
                str(layout_path),
                str(corpus_path),
                "--max-iterations",
                "0",
            ]
        )

    assert exc_info.value.code == 2