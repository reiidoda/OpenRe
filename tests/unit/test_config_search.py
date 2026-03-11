from __future__ import annotations

from agent_workbench.optimizer.config_search import WeightedObjectiveRanker
from agent_workbench.optimizer.config_search import WeightedObjectiveSearch


def test_weighted_objective_ranker_respects_configurable_weights() -> None:
    candidates = [
        {
            "candidate_id": "cand_quality",
            "task_quality": 0.95,
            "trace_quality": 0.85,
            "safety_compliance": 0.45,
            "latency_score": 0.40,
            "cost_efficiency": 0.30,
        },
        {
            "candidate_id": "cand_safety",
            "task_quality": 0.70,
            "trace_quality": 0.55,
            "safety_compliance": 0.95,
            "latency_score": 0.70,
            "cost_efficiency": 0.60,
        },
    ]

    default_ranker = WeightedObjectiveRanker()
    default_best = default_ranker.optimize(candidates)
    assert default_best["candidate_id"] == "cand_quality"

    safety_ranker = WeightedObjectiveRanker.from_config(
        {
            "weights": {
                "task_quality": 0.10,
                "trace_quality": 0.10,
                "safety_compliance": 0.60,
                "latency_score": 0.10,
                "cost_efficiency": 0.10,
            }
        }
    )
    safety_best = safety_ranker.optimize(candidates)
    assert safety_best["candidate_id"] == "cand_safety"


def test_weighted_objective_ranker_is_stable_for_ties() -> None:
    ranker = WeightedObjectiveRanker()
    candidates = [
        {"candidate_id": "cand_b", "task_quality": 1.0},
        {"candidate_id": "cand_a", "task_quality": 1.0},
    ]

    ranking_ids = [item["candidate_id"] for item in ranker.rank(candidates)]
    assert ranking_ids == ["cand_a", "cand_b"]
    assert ranker.optimize(candidates)["candidate_id"] == "cand_a"


def test_weighted_objective_search_legacy_fields_and_breakdown() -> None:
    search = WeightedObjectiveSearch(
        quality_w=0.7,
        trace_w=0.1,
        safety_w=0.1,
        latency_w=0.05,
        cost_w=0.05,
    )
    candidate = {
        "candidate_id": "cand_legacy",
        "task_quality": 0.8,
        "trace_quality": 0.6,
        "safety_compliance": 1.0,
        "latency_score": 0.5,
        "cost_efficiency": 0.4,
    }

    breakdown = search.score_breakdown(candidate)
    assert breakdown["task_quality"] == 0.56
    assert breakdown["trace_quality"] == 0.06
    assert breakdown["safety_compliance"] == 0.1
    assert breakdown["latency_score"] == 0.025
    assert breakdown["cost_efficiency"] == 0.02
    assert search.score(candidate) == 0.765
