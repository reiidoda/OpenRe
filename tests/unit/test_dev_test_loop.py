from __future__ import annotations

import json
from pathlib import Path

from agent_workbench.optimizer.config_search import WeightedObjectiveRanker
from agent_workbench.optimizer.dev_test_loop import DevTestOptimizationLoop


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n"
    path.write_text(payload, encoding="utf-8")


def _build_dataset(root: Path) -> None:
    _write_jsonl(
        root / "tasks.jsonl",
        [
            {
                "task_id": "ra_001",
                "instruction": "Task 1",
                "modality": "text",
                "risk_label": "LOW",
                "tags": ["dev"],
            },
            {
                "task_id": "ra_002",
                "instruction": "Task 2",
                "modality": "text",
                "risk_label": "LOW",
                "tags": ["dev"],
            },
            {
                "task_id": "ra_003",
                "instruction": "Task 3",
                "modality": "text",
                "risk_label": "LOW",
                "tags": ["test"],
            },
        ],
    )
    _write_jsonl(root / "splits" / "dev.jsonl", [{"task_id": "ra_001"}, {"task_id": "ra_002"}])
    _write_jsonl(root / "splits" / "test.jsonl", [{"task_id": "ra_003"}])


def _evaluate(candidate: dict[str, object], _tasks: list[object], split: str) -> dict[str, float]:
    split_metrics = candidate.get(f"{split}_metrics", {})
    if not isinstance(split_metrics, dict):
        return {}
    return {
        "task_quality": float(split_metrics.get("task_quality", 0.0)),
        "trace_quality": float(split_metrics.get("trace_quality", 0.0)),
        "safety_compliance": float(split_metrics.get("safety_compliance", 0.0)),
        "latency_score": float(split_metrics.get("latency_score", 0.0)),
        "cost_efficiency": float(split_metrics.get("cost_efficiency", 0.0)),
    }


def test_dev_split_drives_candidate_selection(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset"
    _build_dataset(dataset)
    loop = DevTestOptimizationLoop(ranker=WeightedObjectiveRanker())
    result = loop.run(
        dataset_path=str(dataset),
        candidates=[
            {
                "candidate_id": "cand_a",
                "dev_metrics": {"task_quality": 0.9, "trace_quality": 0.8},
                "test_metrics": {"task_quality": 0.85, "trace_quality": 0.75},
            },
            {
                "candidate_id": "cand_b",
                "dev_metrics": {"task_quality": 0.7, "trace_quality": 0.9},
                "test_metrics": {"task_quality": 0.9, "trace_quality": 0.9},
            },
        ],
        evaluate_candidate=_evaluate,
    )

    assert result.selected_candidate_id == "cand_a"
    assert result.dev.ranking[0] == "cand_a"


def test_test_split_isolated_and_recorded_separately(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset"
    _build_dataset(dataset)
    loop = DevTestOptimizationLoop(ranker=WeightedObjectiveRanker())
    result = loop.run(
        dataset_path=str(dataset),
        candidates=[
            {
                "candidate_id": "cand_a",
                "dev_metrics": {"task_quality": 0.9, "trace_quality": 0.8},
                "test_metrics": {"task_quality": 0.85, "trace_quality": 0.75},
            },
            {
                "candidate_id": "cand_b",
                "dev_metrics": {"task_quality": 0.7, "trace_quality": 0.9},
                "test_metrics": {"task_quality": 0.9, "trace_quality": 0.9},
            },
        ],
        evaluate_candidate=_evaluate,
    )

    assert result.dev.run_id.startswith("optdev_")
    assert result.test.run_id.startswith("opttest_")
    assert result.dev.run_id != result.test.run_id
    assert result.dev.task_ids == ["ra_001", "ra_002"]
    assert result.test.task_ids == ["ra_003"]
    assert result.test.ranking == [result.selected_candidate_id]
    assert list(result.test.candidate_scores.keys()) == [result.selected_candidate_id]


def test_final_output_indicates_candidate_promotion_status(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset"
    _build_dataset(dataset)
    loop = DevTestOptimizationLoop(
        ranker=WeightedObjectiveRanker(),
        min_test_score=0.80,
        max_dev_test_drop=0.02,
    )
    result = loop.run(
        dataset_path=str(dataset),
        candidates=[
            {
                "candidate_id": "cand_a",
                "dev_metrics": {
                    "task_quality": 0.95,
                    "trace_quality": 0.9,
                    "safety_compliance": 1.0,
                    "latency_score": 0.9,
                    "cost_efficiency": 0.9,
                },
                "test_metrics": {
                    "task_quality": 0.70,
                    "trace_quality": 0.7,
                    "safety_compliance": 0.9,
                    "latency_score": 0.7,
                    "cost_efficiency": 0.7,
                },
            }
        ],
        evaluate_candidate=_evaluate,
    )

    assert result.promoted is False
    assert (
        "below promotion threshold" in result.promotion_reason or "drop" in result.promotion_reason
    )
