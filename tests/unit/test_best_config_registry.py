from __future__ import annotations

import os
from pathlib import Path

from agent_workbench.optimizer.best_config_registry import BestConfigRegistry


def test_registry_stores_config_id_score_breakdown_and_timestamp(tmp_path: Path) -> None:
    store_path = tmp_path / "state" / "best_configs.json"
    registry = BestConfigRegistry(store_path=store_path)

    record = registry.set(
        "research_assistant_v1",
        "candidate_a",
        score_breakdown={"task_quality": 0.42, "trace_quality": 0.18},
        objective_score=0.78,
        timestamp="2026-03-12T12:00:00+00:00",
        metadata={"source": "optimize"},
    )

    assert record["config_id"] == "candidate_a"
    assert record["score_breakdown"] == {"task_quality": 0.42, "trace_quality": 0.18}
    assert record["objective_score"] == 0.78
    assert record["updated_at"] == "2026-03-12T12:00:00+00:00"
    assert record["metadata"] == {"source": "optimize"}

    reloaded = BestConfigRegistry(store_path=store_path)
    assert reloaded.get("research_assistant_v1") == record


def test_registry_update_is_atomic_using_replace(monkeypatch, tmp_path: Path) -> None:
    store_path = tmp_path / "state" / "best_configs.json"
    registry = BestConfigRegistry(store_path=store_path)

    replace_calls: list[tuple[str, str]] = []
    original_replace = os.replace

    def tracked_replace(src: str | Path, dst: str | Path) -> None:
        replace_calls.append((str(src), str(dst)))
        original_replace(src, dst)

    monkeypatch.setattr(
        "agent_workbench.optimizer.best_config_registry.os.replace", tracked_replace
    )

    registry.set(
        "research_assistant_v1",
        "candidate_a",
        score_breakdown={"task_quality": 0.4},
        objective_score=0.4,
        timestamp="2026-03-12T12:00:00+00:00",
    )

    assert replace_calls
    assert replace_calls[0][1] == str(store_path)


def test_registry_get_returns_none_when_missing(tmp_path: Path) -> None:
    store_path = tmp_path / "state" / "best_configs.json"
    registry = BestConfigRegistry(store_path=store_path)
    assert registry.get("missing_dataset") is None
