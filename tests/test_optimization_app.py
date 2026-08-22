# tests/test_optimization_app.py

import pytest

from app.optimization_app import OptimizationApp
from models.corpus import Corpus
from models.corpus_entry import CorpusEntry
from models.layout import Layout
from models.optimization_result import OptimizationResult


def make_layout() -> Layout:
    return Layout(
        name="Optimization App Test",
        version="0.1.0",
        layer="L0",
        description="Optimization application test layout",
        mapping={
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
        },
    )


def make_corpus() -> Corpus:
    return Corpus(
        entries=(
            CorpusEntry(
                text=(
                    "THE QUICK BROWN FOX JUMPS "
                    "OVER THE LAZY DOG"
                ),
            ),
        ),
    )


def test_app_max_iterations():
    app = OptimizationApp(
        max_iterations=3,
    )

    assert app.max_iterations == 3


def test_app_rejects_negative_max_iterations():
    with pytest.raises(ValueError):
        OptimizationApp(
            max_iterations=-1,
        )


def test_app_returns_optimization_result():
    app = OptimizationApp(
        max_iterations=1,
    )

    result = app.optimize(
        layout=make_layout(),
        corpus=make_corpus(),
    )

    assert isinstance(
        result,
        OptimizationResult,
    )


def test_app_result_is_valid():
    app = OptimizationApp(
        max_iterations=1,
    )

    result = app.optimize(
        layout=make_layout(),
        corpus=make_corpus(),
    )

    assert result.initial_evaluation.is_valid is True
    assert result.final_evaluation.is_valid is True


def test_app_does_not_worsen_score():
    app = OptimizationApp(
        max_iterations=1,
    )

    result = app.optimize(
        layout=make_layout(),
        corpus=make_corpus(),
    )

    assert result.initial_score is not None
    assert result.final_score is not None

    assert (
        result.final_score
        <= result.initial_score
    )


def test_optimize_text():
    app = OptimizationApp(
        max_iterations=1,
    )

    result = app.optimize_text(
        layout=make_layout(),
        text="HELLO WORLD",
    )

    assert isinstance(
        result,
        OptimizationResult,
    )

    assert result.final_score is not None


def test_format_result():
    app = OptimizationApp(
        max_iterations=0,
    )

    result = app.optimize(
        layout=make_layout(),
        corpus=make_corpus(),
    )

    report = app.format_result(
        result
    )

    assert isinstance(report, str)
    assert "Optimization Result" in report
    assert "Initial score:" in report
    assert "Final score:" in report