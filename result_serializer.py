from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from models.layout import Layout
from models.multi_start_optimization_result import (
    MultiStartOptimizationResult,
)
from models.search_mode import SearchMode


def serialize_best_result(
    *,
    result: MultiStartOptimizationResult,
    source_layout: Layout,
    mode: SearchMode,
    seed: int,
    max_iterations: int,
    corpus_path: str | Path,
    corpus_sha256: str,
) -> dict[str, Any]:
    best = result.best_result

    if best is None:
        raise ValueError(
            "result has no scored optimization result"
        )

    candidate_score = (
        best.final_evaluation.candidate_score
    )

    if candidate_score is None:
        raise ValueError(
            "best result has no candidate score"
        )

    weights = candidate_score.weights

    return {
        "schema_version": 1,
        "search": {
            "mode": mode.value,
            "runs": result.run_count,
            "max_iterations": max_iterations,
            "seed": seed,
        },
        "source": {
            "layout": {
                "name": source_layout.name,
                "version": source_layout.version,
                "layer": source_layout.layer,
                "description": (
                    source_layout.description
                ),
                "mapping": dict(
                    source_layout.mapping
                ),
            },
            "corpus": {
                "path": str(corpus_path),
                "sha256": corpus_sha256,
            },
        },
        "result": {
            "initial_score": best.initial_score,
            "final_score": best.final_score,
            "improvement": best.improvement,
            "iterations": best.iteration_count,
            "score_components": {
                "transition": (
                    candidate_score.transition_score
                ),
                "trigram": (
                    candidate_score.trigram_score
                ),
                "finger_load": (
                    candidate_score.finger_load_score
                ),
                "position": (
                    candidate_score.position_score
                ),
                "weighted_transition": (
                    candidate_score
                    .weighted_transition_score
                ),
                "weighted_trigram": (
                    candidate_score
                    .weighted_trigram_score
                ),
                "weighted_finger_load": (
                    candidate_score
                    .weighted_finger_load_score
                ),
                "weighted_position": (
                    candidate_score
                    .weighted_position_score
                ),
                "total": candidate_score.total,
            },
            "score_weights": {
                "transition": (
                    weights.transition_weight
                ),
                "trigram": (
                    weights.trigram_weight
                ),
                "finger_load": (
                    weights.finger_load_weight
                ),
                "position": (
                    weights.position_weight
                ),
            },
            "layout": dict(
                best.final_evaluation.layout.mapping
            ),
        },
    }


def write_result_json(
    *,
    path: str | Path,
    data: dict[str, Any],
) -> None:
    path = Path(path)

    path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
