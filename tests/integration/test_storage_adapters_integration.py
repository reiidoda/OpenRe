from __future__ import annotations

from pathlib import Path

from agent_workbench.adapters.storage.filesystem_store import FilesystemStore
from agent_workbench.adapters.storage.sqlite_store import SqliteStore
from agent_workbench.orchestration.runner import Runner


def test_filesystem_store_persists_reports_and_traces_by_run_id(tmp_path: Path) -> None:
    store = FilesystemStore(tmp_path / "artifacts")
    run_id = "run_store_001"

    report_path = store.put_run_report(run_id, "v1/report.json", '{"ok": true}')
    trace_path = store.put_run_trace(run_id, '{"kind":"completed"}\n')

    report_file = Path(report_path)
    trace_file = Path(trace_path)
    assert report_file.exists()
    assert trace_file.exists()
    assert report_file.relative_to(store.root) == Path("reports") / run_id / "v1" / "report.json"
    assert trace_file.relative_to(store.root) == Path("traces") / run_id / "trace.jsonl"
    assert store.get_run_report(run_id, "v1/report.json") == '{"ok": true}'
    assert store.get_run_trace(run_id) == '{"kind":"completed"}\n'


def test_sqlite_store_roundtrip_run_metadata_from_runner(tmp_path: Path) -> None:
    artifact_root = tmp_path / "artifacts"
    runner = Runner(artifact_root=artifact_root)
    result = runner.run(
        dataset="datasets/research_assistant_v1",
        config_paths=[
            "configs/agents/research_basic.yaml",
            "configs/agents/research_multimodal.yaml",
        ],
    )

    run_id = str(result["run_id"])
    sqlite_store = SqliteStore(artifact_root / "state" / "runs.db")
    metadata = sqlite_store.get_run_metadata(run_id)

    assert metadata is not None
    assert metadata["run_id"] == run_id
    assert metadata["dataset_id"] == "research_assistant_v1"
    assert metadata["status"] == "completed"
    assert metadata["task_runs"] == 10
    assert metadata["config_ids"] == ["research_basic", "research_multimodal"]
    assert metadata["artifacts"] == result["artifacts"]
    assert metadata["trace_path"] == result["trace_path"]
