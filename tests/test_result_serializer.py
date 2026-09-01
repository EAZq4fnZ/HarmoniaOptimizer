from __future__ import annotations

import json
from pathlib import Path

import pytest

from models.candidate_evaluation import CandidateEvaluation
from models.candidate_score import (
    CandidateScore,
    CandidateScoreWeights,
)
from models.constraint_evaluation import ConstraintEvaluation
from models.layout import Layout
from models.multi_start_optimization_result import (
    MultiStartOptimizationResult,
)
from models.optimization_result import OptimizationResult
from models.search_mode import SearchMode
from result_serializer import serialize_best_result


def make_layout() -> Layout:
    mapping = {
        chr(ord("A") + index): f"P-{index}"
        for index in range(26)
    }

    return Layout(
        name="Harmonia Test",
        version="1",
        layer="L0",
        description="test layout",
        mapping=mapping,
    )


def make_result() -> MultiStartOptimizationResult:
    layout = make_layout()

    score = CandidateScore(
        transition_score=1.0,
        trigram_score=-0.5,
        finger_load_score=0.25,
        position_score=0.1,
        weights=CandidateScoreWeights(
            transition_weight=1.0,
            trigram_weight=1.0,
            finger_load_weight=2.0,
            position_weight=5.0,
        ),
    )

    evaluation = CandidateEvaluation(
        layout=layout,
        constraint_evaluation=ConstraintEvaluation(
            violations=(),
        ),
        layout_evaluation=None,
        candidate_score=score,
    )

    result = OptimizationResult(
        initial_evaluation=evaluation,
        final_evaluation=evaluation,
        steps=(),
    )

    return MultiStartOptimizationResult(
        results=(result,)
    )


def test_serialize_best_result() -> None:
    result = make_result()

    data = serialize_best_result(
        result=result,
        source_layout=make_layout(),
        mode=SearchMode.FAST,
        seed=12345,
        max_iterations=20,
        corpus_path="corpus.txt",
        corpus_sha256="abc123",
    )

    assert data["schema_version"] == 1

    assert data["search"] == {
        "mode": "fast",
        "runs": 1,
        "max_iterations": 20,
        "seed": 12345,
    }

    assert data["source"]["layout"] == {
        "name": "Harmonia Test",
        "version": "1",
        "layer": "L0",
        "description": "test layout",
        "mapping": make_layout().mapping,
    }

    assert data["source"]["corpus"] == {
        "path": "corpus.txt",
        "sha256": "abc123",
    }

    result_data = data["result"]

    assert result_data["initial_score"] == 1.5
    assert result_data["final_score"] == 1.5
    assert result_data["improvement"] == 0.0
    assert result_data["iterations"] == 0

    assert result_data["score_components"] == {
        "transition": 1.0,
        "trigram": -0.5,
        "finger_load": 0.25,
        "position": 0.1,
        "weighted_transition": 1.0,
        "weighted_trigram": -0.5,
        "weighted_finger_load": 0.5,
        "weighted_position": 0.5,
        "total": 1.5,
    }

    assert (
        result_data["layout"]
        == result.best_result.final_evaluation.layout.mapping
    )


def test_serialize_best_result_uses_explicit_source_layout() -> None:
    result = make_result()

    source_mapping = {
        chr(ord("A") + index): f"P-{(index + 1) % 26}"
        for index in range(26)
    }

    source_layout = Layout(
        name="Source Layout",
        version="source-1",
        layer="L0",
        description="original source layout",
        mapping=source_mapping,
    )

    best = result.best_result

    assert best is not None

    initial_mapping = (
        best.initial_evaluation.layout.mapping
    )

    assert source_layout.mapping != initial_mapping

    data = serialize_best_result(
        result=result,
        source_layout=source_layout,
        mode=SearchMode.FAST,
        seed=12345,
        max_iterations=20,
        corpus_path="corpus.txt",
        corpus_sha256="abc123",
    )

    assert (
        data["source"]["layout"]["mapping"]
        == source_layout.mapping
    )

    assert (
        data["source"]["layout"]["mapping"]
        != initial_mapping
    )

    assert data["source"]["layout"]["name"] == (
        "Source Layout"
    )

    assert (
        data["result"]["layout"]
        == best.final_evaluation.layout.mapping
    )


def test_serialize_best_result_includes_weights() -> None:
    data = serialize_best_result(
        result=make_result(),
        source_layout=make_layout(),
        mode=SearchMode.FAST,
        seed=12345,
        max_iterations=20,
        corpus_path="corpus.txt",
        corpus_sha256="abc123",
    )

    assert data["result"]["score_weights"] == {
        "transition": 1.0,
        "trigram": 1.0,
        "finger_load": 2.0,
        "position": 5.0,
    }


def test_serialize_best_result_rejects_unscored_result() -> None:
    layout = make_layout()

    evaluation = CandidateEvaluation(
        layout=layout,
        constraint_evaluation=ConstraintEvaluation(
            violations=(),
        ),
        layout_evaluation=None,
        candidate_score=None,
    )

    optimization_result = OptimizationResult(
        initial_evaluation=evaluation,
        final_evaluation=evaluation,
        steps=(),
    )

    result = MultiStartOptimizationResult(
        results=(optimization_result,)
    )

    assert result.best_result is None

    with pytest.raises(
        ValueError,
        match="result has no scored optimization result",
    ):
        serialize_best_result(
            result=result,
            source_layout=layout,
            mode=SearchMode.FAST,
            seed=12345,
            max_iterations=20,
            corpus_path="corpus.txt",
            corpus_sha256="abc123",
        )


def test_write_result_json(
    tmp_path: Path,
) -> None:
    from result_serializer import (
        write_result_json,
    )

    data = serialize_best_result(
        result=make_result(),
        source_layout=make_layout(),
        mode=SearchMode.FAST,
        seed=12345,
        max_iterations=20,
        corpus_path="corpus.txt",
        corpus_sha256="abc123",
    )

    path = tmp_path / "result.json"

    write_result_json(
        path=path,
        data=data,
    )

    assert path.exists()

    loaded = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    assert loaded == data
