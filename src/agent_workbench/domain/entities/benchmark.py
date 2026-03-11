"""Benchmark report aggregate entity."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class BenchmarkReport:
    dataset_id: str
    compared_configs: list[str]
    summary_table: list[dict[str, object]] = field(default_factory=list)
    per_task_scores: dict[str, dict[str, float]] = field(default_factory=dict)
    failure_clusters: dict[str, int] = field(default_factory=dict)
    failure_cluster_details: list[dict[str, object]] = field(default_factory=list)
    best_config: str | None = None
    exported_artifacts: list[str] = field(default_factory=list)
