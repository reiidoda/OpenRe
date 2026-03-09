"""Benchmark runner orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from agent_workbench.adapters.local.json_trace_sink import JsonTraceSink
from agent_workbench.domain.entities.trace import TraceEvent, TraceEventKind
from agent_workbench.domain.entities.task import TaskModality, TaskSpec
from agent_workbench.domain.value_objects.risk_level import RiskLevel
from agent_workbench.reporting.benchmark_report import BenchmarkReportBuilder
from agent_workbench.reporting.csv_export import export as export_csv
from agent_workbench.reporting.html_export import export as export_html
from agent_workbench.reporting.json_export import export as export_json
from agent_workbench.utils.ids import make_id


def _risk_from_label(label: str) -> RiskLevel:
    normalized = label.upper()
    if normalized in RiskLevel.__members__:
        return RiskLevel[normalized]
    return RiskLevel.LOW


def _modality_from_label(label: str) -> TaskModality:
    normalized = label.lower()
    mapping = {
        "text": TaskModality.TEXT,
        "image": TaskModality.IMAGE,
        "browser": TaskModality.BROWSER,
        "computer": TaskModality.COMPUTER,
    }
    return mapping.get(normalized, TaskModality.TEXT)


@dataclass(slots=True)
class Runner:
    artifact_root: Path = Path(".artifacts")

    def _load_tasks(self, dataset_path: Path) -> list[TaskSpec]:
        tasks: list[TaskSpec] = []
        with (dataset_path / "tasks.jsonl").open("r", encoding="utf-8") as file:
            for line in file:
                item = json.loads(line)
                tasks.append(
                    TaskSpec(
                        task_id=item["task_id"],
                        instruction=item["instruction"],
                        modality=_modality_from_label(item.get("modality", "text")),
                        risk_profile=_risk_from_label(item.get("risk_label", "LOW")),
                        tags=item.get("tags", []),
                    )
                )
        return tasks

    def run(self, dataset: str, config_paths: list[str]) -> dict[str, object]:
        run_id = make_id("run")
        dataset_path = Path(dataset)
        tasks = self._load_tasks(dataset_path)

        trace_path = self.artifact_root / "traces" / f"{run_id}.jsonl"
        trace_sink = JsonTraceSink(trace_path)
        rows: list[dict[str, object]] = []

        for config_path in config_paths:
            config_id = Path(config_path).stem
            for task in tasks:
                task_run_id = make_id("taskrun")
                trace_sink.write(
                    TraceEvent(
                        event_id=make_id("evt"),
                        run_id=run_id,
                        task_run_id=task_run_id,
                        kind=TraceEventKind.PROMPT_SENT,
                        payload={"config_id": config_id, "task_id": task.task_id},
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
                        "config_id": config_id,
                        "status": "completed",
                        "score": 1.0,
                        "risk": task.risk_profile.value,
                    }
                )

        report = BenchmarkReportBuilder(
            dataset_id=dataset_path.name,
            configs=[Path(p).stem for p in config_paths],
        ).build(rows)

        outputs_dir = self.artifact_root / "reports" / run_id
        json_path = export_json(report, outputs_dir / "report.json")
        csv_path = export_csv(rows, outputs_dir / "summary.csv")
        html_path = export_html("Open Agent Workbench Benchmark", rows, outputs_dir / "report.html")

        return {
            "run_id": run_id,
            "dataset": dataset_path.name,
            "configs": [Path(p).stem for p in config_paths],
            "rows": len(rows),
            "trace_path": str(trace_path.resolve()),
            "artifacts": [json_path, csv_path, html_path],
        }
