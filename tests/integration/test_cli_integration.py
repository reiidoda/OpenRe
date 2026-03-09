import json
from pathlib import Path

from agent_workbench.app.cli import build_parser, main


def _parse_stdout_json(captured: str) -> dict[str, object]:
    return json.loads(captured.strip())


def test_help_lists_v1_commands() -> None:
    help_text = build_parser().format_help()
    for command in ["run", "compare", "eval", "optimize", "approve", "report"]:
        assert command in help_text


def test_cli_run_outputs_json(capsys, tmp_path: Path) -> None:
    code = main(
        [
            "--artifact-root",
            str(tmp_path / "artifacts"),
            "run",
            "--dataset",
            "datasets/research_assistant_v1",
            "--config",
            "configs/agents/research_basic.yaml",
        ]
    )
    assert code == 0

    payload = _parse_stdout_json(capsys.readouterr().out)
    assert payload["command"] == "run"
    assert payload["rows"] == 5
    assert payload["dataset"] == "research_assistant_v1"


def test_cli_compare_outputs_json(capsys, tmp_path: Path) -> None:
    code = main(
        [
            "--artifact-root",
            str(tmp_path / "artifacts"),
            "compare",
            "--dataset",
            "datasets/research_assistant_v1",
            "--configs",
            "configs/agents/research_basic.yaml",
            "configs/agents/research_multimodal.yaml",
        ]
    )
    assert code == 0

    payload = _parse_stdout_json(capsys.readouterr().out)
    assert payload["command"] == "compare"
    assert payload["rows"] == 10
    assert payload["configs"] == ["research_basic", "research_multimodal"]


def test_cli_eval_outputs_json(capsys) -> None:
    code = main(["eval", "--run-id", "run_123"])
    assert code == 0

    payload = _parse_stdout_json(capsys.readouterr().out)
    assert payload == {
        "command": "eval",
        "message": "Eval pipeline scaffolded",
        "run_id": "run_123",
        "status": "planned",
    }


def test_cli_optimize_outputs_json(capsys) -> None:
    code = main(
        [
            "optimize",
            "--dataset",
            "datasets/research_assistant_v1",
            "--search-space",
            "configs/agents/research_basic.yaml",
        ]
    )
    assert code == 0

    payload = _parse_stdout_json(capsys.readouterr().out)
    assert payload == {
        "command": "optimize",
        "dataset": "datasets/research_assistant_v1",
        "message": "Optimizer pipeline scaffolded",
        "search_space": "configs/agents/research_basic.yaml",
        "status": "planned",
    }


def test_cli_approve_outputs_json(capsys) -> None:
    code = main(["approve", "--request-id", "apr_123", "--decision", "approve"])
    assert code == 0

    payload = _parse_stdout_json(capsys.readouterr().out)
    assert payload == {
        "command": "approve",
        "decision": "approve",
        "request_id": "apr_123",
        "status": "recorded",
    }


def test_cli_report_outputs_json(capsys, tmp_path: Path) -> None:
    artifact_root = tmp_path / "artifacts"
    code = main(
        [
            "--artifact-root",
            str(artifact_root),
            "report",
            "--run-id",
            "run_123",
            "--format",
            "html",
        ]
    )
    assert code == 0

    payload = _parse_stdout_json(capsys.readouterr().out)
    assert payload["command"] == "report"
    assert payload["run_id"] == "run_123"
    assert payload["format"] == "html"
    assert payload["path"] == str(artifact_root / "reports" / "run_123" / "report.html")
