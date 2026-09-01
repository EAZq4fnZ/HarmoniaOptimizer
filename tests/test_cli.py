from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from app.cli import load_corpus, main, parse_args
from file_digest import sha256_file
from models.search_mode import SearchMode


def test_parse_args() -> None:
    args = parse_args(
        [
            "--layout",
            "layout.json",
            "--corpus",
            "corpus.txt",
            "--mode",
            "deep",
            "--seed",
            "12345",
            "--output",
            "result.json",
        ]
    )

    assert args.layout == Path("layout.json")
    assert args.corpus == Path("corpus.txt")
    assert args.mode is SearchMode.DEEP
    assert args.seed == 12345
    assert args.output == Path("result.json")


def test_parse_args_uses_defaults() -> None:
    args = parse_args(
        [
            "--layout",
            "layout.json",
            "--corpus",
            "corpus.txt",
        ]
    )

    assert args.mode is SearchMode.STANDARD
    assert args.seed == 20260901
    assert args.output is None


def test_load_corpus(
    tmp_path: Path,
) -> None:
    path = tmp_path / "corpus.txt"

    path.write_text(
        "harmonia test corpus",
        encoding="utf-8",
    )

    corpus = load_corpus(path)

    assert len(corpus.entries) == 1
    assert (
        corpus.entries[0].text
        == "harmonia test corpus"
    )



def test_main_rejects_missing_layout_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    layout_path = tmp_path / "missing-layout.json"
    corpus_path = tmp_path / "corpus.txt"
    corpus_path.write_text(
        "harmonia",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "app.cli.parse_args",
        lambda: argparse.Namespace(
            layout=layout_path,
            corpus=corpus_path,
            mode=SearchMode.FAST,
            seed=1,
        ),
    )

    exit_code = main()
    captured = capsys.readouterr()

    assert exit_code == 2
    assert (
        f"error: layout file not found: {layout_path}"
        in captured.err
    )


def test_main_rejects_missing_corpus_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    layout_path = tmp_path / "layout.json"
    layout_path.write_text(
        "{}",
        encoding="utf-8",
    )
    corpus_path = tmp_path / "missing-corpus.txt"

    monkeypatch.setattr(
        "app.cli.parse_args",
        lambda: argparse.Namespace(
            layout=layout_path,
            corpus=corpus_path,
            mode=SearchMode.FAST,
            seed=1,
        ),
    )

    exit_code = main()
    captured = capsys.readouterr()

    assert exit_code == 2
    assert (
        f"error: corpus file not found: {corpus_path}"
        in captured.err
    )


def test_main_writes_output_when_requested(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    layout_path = tmp_path / "layout.json"
    corpus_path = tmp_path / "corpus.txt"
    output_path = tmp_path / "result.json"

    layout_path.write_text(
        "{}",
        encoding="utf-8",
    )
    corpus_path.write_text(
        "harmonia",
        encoding="utf-8",
    )

    source_layout = object()
    final_layout = argparse.Namespace(
        mapping={
            "A": "P-0",
        }
    )
    best = argparse.Namespace(
        final_score=-1.0,
        final_evaluation=argparse.Namespace(
            layout=final_layout,
        ),
    )
    optimization_result = argparse.Namespace(
        best_result=best,
        run_count=2,
    )

    monkeypatch.setattr(
        "app.cli.parse_args",
        lambda: argparse.Namespace(
            layout=layout_path,
            corpus=corpus_path,
            mode=SearchMode.FAST,
            seed=12345,
            output=output_path,
        ),
    )

    monkeypatch.setattr(
        "app.cli.OptimizationConfigLoader.load",
        lambda path: object(),
    )
    monkeypatch.setattr(
        "app.cli.ConstraintConfigLoader.load",
        lambda path: object(),
    )
    monkeypatch.setattr(
        "app.cli.SearchBudgetProfilesLoader.load",
        lambda path: object(),
    )
    monkeypatch.setattr(
        "app.cli.Layout.load",
        lambda path: source_layout,
    )

    app = argparse.Namespace(
        optimize_with_mode=(
            lambda **kwargs: optimization_result
        )
    )

    monkeypatch.setattr(
        "app.cli.OptimizationApp",
        lambda **kwargs: app,
    )

    serialized = {
        "schema_version": 1,
    }
    calls: dict[str, object] = {}

    def fake_serialize_best_result(
        **kwargs: object,
    ) -> dict[str, object]:
        calls["serialize"] = kwargs
        return serialized

    def fake_write_result_json(
        **kwargs: object,
    ) -> None:
        calls["write"] = kwargs

    monkeypatch.setattr(
        "app.cli.serialize_best_result",
        fake_serialize_best_result,
        raising=False,
    )
    monkeypatch.setattr(
        "app.cli.write_result_json",
        fake_write_result_json,
        raising=False,
    )

    exit_code = main()

    assert exit_code == 0

    serialize_call = calls["serialize"]
    assert isinstance(
        serialize_call,
        dict,
    )
    assert serialize_call == {
        "result": optimization_result,
        "source_layout": source_layout,
        "mode": SearchMode.FAST,
        "seed": 12345,
        "corpus_path": corpus_path,
        "corpus_sha256": sha256_file(
            corpus_path
        ),
    }

    write_call = calls["write"]
    assert isinstance(
        write_call,
        dict,
    )
    assert write_call == {
        "path": output_path,
        "data": serialized,
    }
