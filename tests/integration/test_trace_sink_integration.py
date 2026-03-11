from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

from agent_workbench.orchestration.runner import Runner


REQUIRED_TRACE_FIELDS = {
    "event_id",
    "run_id",
    "task_run_id",
    "kind",
    "timestamp",
    "payload",
}


def test_runner_creates_run_scoped_trace_file(tmp_path: Path) -> None:
    artifact_root = tmp_path / "artifacts"
    runner = Runner(artifact_root=artifact_root)

    result = runner.run(
        dataset="datasets/research_assistant_v1",
        config_paths=["configs/agents/research_basic.yaml"],
    )

    run_id = str(result["run_id"])
    trace_path = artifact_root / "traces" / run_id / "trace.jsonl"

    assert trace_path.exists()
    assert trace_path.is_file()
    assert result["trace_path"] == str(trace_path.resolve())


def test_trace_sink_writes_ndjson_with_expected_event_schema(tmp_path: Path) -> None:
    artifact_root = tmp_path / "artifacts"
    runner = Runner(artifact_root=artifact_root)

    result = runner.run(
        dataset="datasets/research_assistant_v1",
        config_paths=["configs/agents/research_basic.yaml"],
    )
    run_id = str(result["run_id"])

    trace_path = artifact_root / "traces" / run_id / "trace.jsonl"
    raw = trace_path.read_text(encoding="utf-8")
    lines = raw.splitlines()

    # Newline-delimited JSON contract: one JSON object per line, trailing newline present.
    assert raw.endswith("\n")
    assert len(lines) == 10  # 5 tasks x 2 events (prompt_sent + completed)
    assert raw.count("\n") == len(lines)

    for line in lines:
        event = json.loads(line)
        assert REQUIRED_TRACE_FIELDS.issubset(event.keys())
        assert event["run_id"] == run_id
        assert isinstance(event["event_id"], str)
        assert isinstance(event["task_run_id"], str)
        assert isinstance(event["payload"], dict)
        assert isinstance(event["kind"], str)

        # Ensure timestamp is machine-parseable ISO format.
        datetime.fromisoformat(str(event["timestamp"]))
