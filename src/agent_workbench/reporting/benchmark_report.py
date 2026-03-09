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


@dataclass(slots=True)
class BenchmarkReportBuilder:
    dataset_id: str
    configs: list[str]

    def build(self, rows: list[dict[str, object]]) -> BenchmarkReport:
        best = None
        if rows:
            best = str(max(rows, key=_score_value).get("config_id"))
        return BenchmarkReport(
            dataset_id=self.dataset_id,
            compared_configs=self.configs,
            summary_table=rows,
            best_config=best,
        )
