"""Benchmark report assembly."""

from __future__ import annotations

from dataclasses import dataclass

from agent_workbench.domain.entities.benchmark import BenchmarkReport


@dataclass(slots=True)
class BenchmarkReportBuilder:
    dataset_id: str
    configs: list[str]

    def build(self, rows: list[dict[str, object]]) -> BenchmarkReport:
        best = None
        if rows:
            best = str(max(rows, key=lambda row: float(row.get("score", 0.0))).get("config_id"))
        return BenchmarkReport(
            dataset_id=self.dataset_id,
            compared_configs=self.configs,
            summary_table=rows,
            best_config=best,
        )
