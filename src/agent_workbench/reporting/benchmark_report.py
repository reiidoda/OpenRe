"""Benchmark report assembly."""

from __future__ import annotations

from dataclasses import dataclass

from agent_workbench.domain.entities.benchmark import BenchmarkReport


def _score_value(row: dict[str, object]) -> float:
    raw = row.get("score", 0.0)
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, str):
        try:
            return float(raw)
        except ValueError:
            return 0.0
    return 0.0


def _per_task_scores(rows: list[dict[str, object]]) -> dict[str, dict[str, float]]:
    scores: dict[str, dict[str, float]] = {}
    for row in rows:
        task_id = str(row.get("task_id", "")).strip()
        config_id = str(row.get("config_id", "")).strip()
        if not task_id or not config_id:
            continue
        scores.setdefault(task_id, {})[config_id] = _score_value(row)
    return scores


def _failure_clusters(rows: list[dict[str, object]]) -> dict[str, int]:
    clusters: dict[str, int] = {}
    for row in rows:
        raw_labels = row.get("failure_labels")
        if not isinstance(raw_labels, list):
            continue
        for label in raw_labels:
            if not isinstance(label, str):
                continue
            key = label.strip()
            if not key:
                continue
            clusters[key] = clusters.get(key, 0) + 1
    return clusters


@dataclass(slots=True)
class BenchmarkReportBuilder:
    dataset_id: str
    configs: list[str]

    def build(self, rows: list[dict[str, object]]) -> BenchmarkReport:
        best = None
        if rows:
            score_by_config: dict[str, list[float]] = {}
            for row in rows:
                config_id = str(row.get("config_id", "")).strip()
                if not config_id:
                    continue
                score_by_config.setdefault(config_id, []).append(_score_value(row))
            if score_by_config:
                best = max(
                    score_by_config.items(),
                    key=lambda item: sum(item[1]) / len(item[1]),
                )[0]
        return BenchmarkReport(
            dataset_id=self.dataset_id,
            compared_configs=self.configs,
            summary_table=rows,
            per_task_scores=_per_task_scores(rows),
            failure_clusters=_failure_clusters(rows),
            best_config=best,
        )
