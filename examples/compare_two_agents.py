from agent_workbench.orchestration.runner import Runner


if __name__ == "__main__":
    runner = Runner()
    print(
        runner.run(
            dataset="datasets/research_assistant_v1",
            config_paths=[
                "configs/agents/research_basic.yaml",
                "configs/agents/research_multimodal.yaml",
            ],
        )
    )
