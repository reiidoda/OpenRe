from __future__ import annotations

from pathlib import Path

from agent_workbench.reporting.html_export import export


def test_html_export_renders_failure_cluster_section_with_trace_link(tmp_path: Path) -> None:
    target = tmp_path / "report.html"
    html_path = export(
        "Benchmark",
        rows=[{"task_id": "ra_001", "config_id": "cfg_a", "score": 0.7}],
        target=target,
        cluster_details=[
            {
                "label": "approval_missing",
                "count": 2,
                "representative": {
                    "task_id": "ra_003",
                    "config_id": "cfg_a",
                    "task_run_id": "taskrun_123",
                    "trace_path": "/tmp/trace.jsonl",
                },
            }
        ],
    )

    assert html_path == str(target.resolve())
    html = target.read_text(encoding="utf-8")
    assert "<h2>Failure Clusters</h2>" in html
    assert "approval_missing" in html
    assert "taskrun_123" in html
    assert "/tmp/trace.jsonl#task_run_id=taskrun_123" in html
