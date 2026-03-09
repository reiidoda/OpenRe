from agent_workbench.optimizer.prompt_sweeper import generate_variants


if __name__ == "__main__":
    for variant in generate_variants("You are a helpful research assistant."):
        print(variant)
