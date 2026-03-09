from agent_workbench.app.cli import main


def test_cli_run_returns_zero() -> None:
    code = main(
        [
            "run",
            "--dataset",
            "datasets/research_assistant_v1",
            "--config",
            "configs/agents/research_basic.yaml",
        ]
    )
    assert code == 0
