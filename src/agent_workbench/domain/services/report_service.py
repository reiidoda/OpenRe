"""Report service."""

from __future__ import annotations

from dataclasses import dataclass

from agent_workbench.domain.entities.benchmark import BenchmarkReport


@dataclass(slots=True)
class ReportService:
    def summarize(self, report: BenchmarkReport) -> dict[str, object]:
        return {
            "dataset_id": report.dataset_id,
            "configs": report.compared_configs,
            "best_config": report.best_config,
            "rows": len(report.summary_table),
        }
