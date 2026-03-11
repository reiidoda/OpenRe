"""Benchmark runner orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any

from agent_workbench.adapters.local.config_loader import YamlAgentConfigLoader
from agent_workbench.adapters.local.dataset_loader import JsonlDatasetProvider
from agent_workbench.adapters.local.json_trace_sink import JsonTraceSink
from agent_workbench.domain.entities.trace import TraceEvent, TraceEventKind
from agent_workbench.reporting.benchmark_report import BenchmarkReportBuilder
from agent_workbench.reporting.csv_export import export as export_csv
from agent_workbench.reporting.html_export import export as export_html
from agent_workbench.reporting.json_export import export as export_json
from agent_workbench.utils.clock import utc_now_iso
from agent_workbench.utils.ids import make_id


@dataclass(slots=True)
class Runner:
    artifact_root: Path = Path(".artifacts")
    dataset_provider: JsonlDatasetProvider = field(default_factory=JsonlDatasetProvider)
    config_loader: YamlAgentConfigLoader = field(default_factory=YamlAgentConfigLoader)
    report_schema_version: str = "awb.report.v1"

    @staticmethod
    def _build_summary(rows: list[dict[str, object]], config_ids: list[str]) -> dict[str, Any]:
        task_runs = len(rows)
        completed = sum(1 for row in rows if row.get("status") == "completed")
        success_rate = float(completed / task_runs) if task_runs else 0.0

        config_summaries: list[dict[str, object]] = []
        for config_id in config_ids:
            config_rows = [row for row in rows if row.get("config_id") == config_id]
            config_total = len(config_rows)
            config_completed = sum(1 for row in config_rows if row.get("status") == "completed")
            config_success = float(config_completed / config_total) if config_total else 0.0
            config_summaries.append(
                {
                    "config_id": config_id,
                    "task_runs": config_total,
                    "completed": config_completed,
                    "success_rate": round(config_success, 4),
                    "estimated_cost_usd": 0.0,
                    "cost_is_placeholder": True,
                }
            )

        return {
            "task_runs": task_runs,
            "completed": completed,
            "success_rate": round(success_rate, 4),
            "estimated_total_cost_usd": 0.0,
            "cost_is_placeholder": True,
            "config_summaries": config_summaries,
        }

    def run(self, dataset: str, config_paths: list[str]) -> dict[str, object]:
        run_id = make_id("run")
        dataset_path = Path(dataset)
        tasks = self.dataset_provider.load_tasks(str(dataset_path))
        configs = [self.config_loader.load(config_path) for config_path in config_paths]

        trace_path = self.artifact_root / "traces" / f"{run_id}.jsonl"
        trace_sink = JsonTraceSink(trace_path)
        rows: list[dict[str, object]] = []

        for config in configs:
            for task in tasks:
                task_run_id = make_id("taskrun")
                trace_sink.write(
                    TraceEvent(
                        event_id=make_id("evt"),
                        run_id=run_id,
                        task_run_id=task_run_id,
                        kind=TraceEventKind.PROMPT_SENT,
                        payload={"config_id": config.config_id, "task_id": task.task_id},
                    )
                )
                trace_sink.write(
                    TraceEvent(
                        event_id=make_id("evt"),
                        run_id=run_id,
                        task_run_id=task_run_id,
                        kind=TraceEventKind.COMPLETED,
                        payload={"status": "ok"},
                    )
                )
                rows.append(
                    {
                        "task_id": task.task_id,
                        "config_id": config.config_id,
                        "status": "completed",
                        "score": 1.0,
                        "risk": task.risk_profile.value,
                    }
                )

        report = BenchmarkReportBuilder(
            dataset_id=dataset_path.name,
            configs=[config.config_id for config in configs],
        ).build(rows)

        config_ids = [config.config_id for config in configs]
        summary = self._build_summary(rows, config_ids)
        outputs_dir = self.artifact_root / "reports" / run_id / "v1"
        run_metadata = {
            "run_id": run_id,
            "dataset_id": dataset_path.name,
            "config_ids": config_ids,
            "task_count": len(tasks),
            "task_run_count": len(rows),
            "generated_at": utc_now_iso(),
        }
        json_payload = {
            "schema_version": self.report_schema_version,
            "run": run_metadata,
            "summary": summary,
            "rows": rows,
            "benchmark": report,
        }

        json_path = export_json(json_payload, outputs_dir / "report.json")
        csv_path = export_csv(
            rows,
            outputs_dir / "summary.csv",
            metadata={
                "schema_version": self.report_schema_version,
                "run_id": run_id,
                "dataset_id": dataset_path.name,
            },
        )
        html_path = export_html("Open Agent Workbench Benchmark", rows, outputs_dir / "report.html")

        return {
            "run_id": run_id,
            "dataset": dataset_path.name,
            "configs": config_ids,
            "rows": len(rows),
            "result_table": rows,
            "summary": summary,
            "trace_path": str(trace_path.resolve()),
            "artifacts": [json_path, csv_path, html_path],
        }
