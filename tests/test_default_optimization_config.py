from config_loader.optimization_config_loader import (
    OptimizationConfigLoader,
)


def test_default_candidate_score_weights() -> None:
    config = OptimizationConfigLoader.load(
        "config/optimization/default.json"
    )

    weights = config.candidate_score_weights

    assert weights.transition_weight == 1.0
    assert weights.trigram_weight == 1.0
    assert weights.finger_load_weight == 1.0
    assert weights.position_weight == 5.0
