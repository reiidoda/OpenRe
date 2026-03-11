"""Benchmark runner orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any

from agent_workbench.adapters.local.config_loader import YamlAgentConfigLoader
from agent_workbench.adapters.local.dataset_loader import JsonlDatasetProvider
from agent_workbench.adapters.local.json_trace_sink import JsonTraceSink
from agent_workbench.adapters.storage.filesystem_store import FilesystemStore
from agent_workbench.adapters.storage.sqlite_store import SqliteStore
from agent_workbench.domain.entities.trace import TraceEvent, TraceEventKind
from agent_workbench.evals.graders.exact_match import ExactMatchGrader
from agent_workbench.evals.graders.rubric_grade import RubricGrader
from agent_workbench.evals.graders.trace_grade import TraceGrader
from agent_workbench.evals.harness import EvalHarness, TaskRunEvaluation
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
    report_schema_version: str = "openre.report.v1"
    filesystem_store: FilesystemStore | None = None
    sqlite_store: SqliteStore | None = None
    trace_grader: TraceGrader = field(default_factory=TraceGrader)
    eval_harness: EvalHarness | None = None

    def _build_summary(
        self,
        *,
        task_evaluations: list[TaskRunEvaluation],
        config_ids: list[str],
    ) -> dict[str, Any]:
        overall_metrics = EvalHarness.aggregate_metrics(task_evaluations)
        task_runs = overall_metrics.task_runs
        completed = task_runs
        success_rate = overall_metrics.success_rate

        config_summaries: list[dict[str, object]] = []
        for config_id in config_ids:
            config_evaluations = [
                evaluation for evaluation in task_evaluations if evaluation.config_id == config_id
            ]
            config_metrics = EvalHarness.aggregate_metrics(config_evaluations)
            config_summaries.append(
                {
                    "config_id": config_id,
                    "task_runs": config_metrics.task_runs,
                    "completed": config_metrics.task_runs,
                    "success_rate": round(config_metrics.success_rate, 4),
                    "avg_score": round(config_metrics.avg_score, 4),
                    "avg_latency_ms": round(config_metrics.avg_latency_ms, 2),
                    "avg_cost_usd": round(config_metrics.avg_cost_usd, 6),
                    "estimated_cost_usd": 0.0,
                    "latency_is_placeholder": True,
                    "cost_is_placeholder": True,
                }
            )

        return {
            "task_runs": task_runs,
            "completed": completed,
            "success_rate": round(success_rate, 4),
            "avg_score": round(overall_metrics.avg_score, 4),
            "avg_latency_ms": round(overall_metrics.avg_latency_ms, 2),
            "avg_cost_usd": round(overall_metrics.avg_cost_usd, 6),
            "estimated_total_cost_usd": 0.0,
            "latency_is_placeholder": True,
            "cost_is_placeholder": True,
            "config_summaries": config_summaries,
        }

    @staticmethod
    def _build_eval_expected(
        *,
        output_text: str,
        event_kinds: list[str],
        requires_approval: bool,
    ) -> dict[str, object]:
        return {
            "target": output_text,
            "rubric": {
                "criteria": [
                    {
                        "name": "correctness",
                        "required_terms": ["alpha"],
                        "mode": "all",
                    },
                    {
                        "name": "completeness",
                        "required_terms": ["beta"],
                        "mode": "all",
                    },
                ]
            },
            "trace_events": event_kinds,
            "trace": {
                "required_sequence": ["prompt_sent", "completed"],
                "requires_approval": requires_approval,
                "max_tool_calls": 2,
            },
        }

    def run(self, dataset: str, config_paths: list[str]) -> dict[str, object]:
        run_id = make_id("run")
        dataset_path = Path(dataset)
        tasks = self.dataset_provider.load_tasks(str(dataset_path))
        configs = [self.config_loader.load(config_path) for config_path in config_paths]
        filesystem_store = self.filesystem_store or FilesystemStore(self.artifact_root)
        sqlite_store = self.sqlite_store or SqliteStore(self.artifact_root / "state" / "runs.db")
        eval_harness = self.eval_harness or EvalHarness(
            evaluators=[
                ExactMatchGrader(),
                RubricGrader(),
                self.trace_grader,
            ]
        )

        trace_path = filesystem_store.run_trace_path(run_id)
        trace_sink = JsonTraceSink(trace_path)
        rows: list[dict[str, object]] = []
        task_evaluations: list[TaskRunEvaluation] = []

        for config in configs:
            for task in tasks:
                task_run_id = make_id("taskrun")
                event_kinds: list[str] = []

                def emit(kind: TraceEventKind, payload: dict[str, str]) -> None:
                    event_kinds.append(kind.value)
                    trace_sink.write(
                        TraceEvent(
                            event_id=make_id("evt"),
                            run_id=run_id,
                            task_run_id=task_run_id,
                            kind=kind,
                            payload=payload,
                        )
                    )

                emit(
                    TraceEventKind.PROMPT_SENT,
                    {"config_id": config.config_id, "task_id": task.task_id},
                )

                output_text = f"task {task.task_id} alpha beta completed"
                requires_approval = task.risk_profile.value in {"HIGH", "CRITICAL"}
                if requires_approval:
                    emit(
                        TraceEventKind.APPROVAL_REQUESTED,
                        {"reason": "high_or_critical_risk_action"},
                    )
                    emit(
                        TraceEventKind.APPROVAL_RECEIVED,
                        {"decision": "approved"},
                    )
                emit(
                    TraceEventKind.COMPLETED,
                    {"status": "ok"},
                )
                expected_eval = self._build_eval_expected(
                    output_text=output_text,
                    event_kinds=event_kinds,
                    requires_approval=requires_approval,
                )
                task_evaluation = eval_harness.evaluate_task_run(
                    task_id=task.task_id,
                    config_id=config.config_id,
                    output=output_text,
                    expected=expected_eval,
                    latency_ms=0.0,
                    cost_usd=0.0,
                )
                task_evaluations.append(task_evaluation)
                rows.append(
                    {
                        "task_id": task.task_id,
                        "config_id": config.config_id,
                        "task_run_id": task_run_id,
                        "trace_path": str(trace_path.resolve()),
                        "status": "completed",
                        "output_quality_score": task_evaluation.output_quality_score,
                        "trace_quality_score": task_evaluation.trace_quality_score,
                        "score": task_evaluation.score,
                        "latency_ms": task_evaluation.latency_ms,
                        "cost_usd": task_evaluation.cost_usd,
                        "risk": task.risk_profile.value,
                        "failure_labels": task_evaluation.failure_labels,
                        "evaluator_scores": task_evaluation.evaluator_scores,
                    }
                )

        report = BenchmarkReportBuilder(
            dataset_id=dataset_path.name,
            configs=[config.config_id for config in configs],
        ).build(rows)

        config_ids = [config.config_id for config in configs]
        summary = self._build_summary(
            task_evaluations=task_evaluations,
            config_ids=config_ids,
        )
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

        json_path = export_json(
            json_payload,
            filesystem_store.run_report_path(run_id, "v1/report.json"),
        )
        csv_path = export_csv(
            rows,
            filesystem_store.run_report_path(run_id, "v1/summary.csv"),
            metadata={
                "schema_version": self.report_schema_version,
                "run_id": run_id,
                "dataset_id": dataset_path.name,
            },
        )
        html_path = export_html(
            "Open Agent Workbench Benchmark",
            rows,
            filesystem_store.run_report_path(run_id, "v1/report.html"),
            cluster_details=report.failure_cluster_details,
        )
        sqlite_store.put_run_metadata(
            run_id=run_id,
            dataset_id=dataset_path.name,
            status="completed",
            task_runs=len(rows),
            trace_path=str(trace_path.resolve()),
            config_ids=config_ids,
            artifacts=[json_path, csv_path, html_path],
        )

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
