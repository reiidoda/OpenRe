from __future__ import annotations

import csv
import json
from pathlib import Path

from agent_workbench.orchestration.runner import Runner


def _artifact_path(artifacts: list[str], suffix: str) -> Path:
    for artifact in artifacts:
        if artifact.endswith(suffix):
            return Path(artifact)
    raise AssertionError(f"Missing artifact with suffix: {suffix}")


def test_json_export_includes_run_metadata_and_rows(tmp_path: Path) -> None:
    runner = Runner(artifact_root=tmp_path / "artifacts")
    result = runner.run(
        dataset="datasets/research_assistant_v1",
        config_paths=[
            "configs/agents/research_basic.yaml",
            "configs/agents/research_multimodal.yaml",
        ],
    )

    run_id = str(result["run_id"])
    report_json = _artifact_path(result["artifacts"], "report.json")
    payload = json.loads(report_json.read_text(encoding="utf-8"))

    assert payload["schema_version"] == "openre.report.v1"
    assert payload["run"]["run_id"] == run_id
    assert payload["run"]["dataset_id"] == "research_assistant_v1"
    assert payload["run"]["config_ids"] == ["research_basic", "research_multimodal"]
    assert payload["run"]["task_count"] == 5
    assert payload["run"]["task_run_count"] == 10
    assert isinstance(payload["run"]["generated_at"], str)
    assert len(payload["rows"]) == 10
    assert payload["summary"]["task_runs"] == 10

    assert report_json.parent.name == "v1"
    assert report_json.parent.parent.name == run_id


def test_csv_export_is_flattened_and_includes_run_columns(tmp_path: Path) -> None:
    runner = Runner(artifact_root=tmp_path / "artifacts")
    result = runner.run(
        dataset="datasets/research_assistant_v1",
        config_paths=[
            "configs/agents/research_basic.yaml",
            "configs/agents/research_multimodal.yaml",
        ],
    )

    run_id = str(result["run_id"])
    summary_csv = _artifact_path(result["artifacts"], "summary.csv")

    with summary_csv.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 10
    first = rows[0]
    assert first["schema_version"] == "openre.report.v1"
    assert first["run_id"] == run_id
    assert first["dataset_id"] == "research_assistant_v1"
    assert first["task_id"] == "ra_001"
    assert first["config_id"] == "research_basic"
    assert first["status"] == "completed"

    assert summary_csv.parent.name == "v1"
    assert summary_csv.parent.parent.name == run_id
