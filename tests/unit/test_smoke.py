from pathlib import Path

from agent_workbench.orchestration.runner import Runner


def test_runner_produces_artifacts(tmp_path: Path) -> None:
    runner = Runner(artifact_root=tmp_path / "artifacts")
    result = runner.run(
        dataset="datasets/research_assistant_v1",
        config_paths=["configs/agents/research_basic.yaml"],
    )

    assert result["rows"] == 5
    for artifact in result["artifacts"]:
        assert Path(artifact).exists()
