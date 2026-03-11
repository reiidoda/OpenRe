from agent_workbench.optimizer.prompt_sweeper import (
    PromptVariantConstraints,
    sweep_prompt_variants_on_dev_tasks,
)


if __name__ == "__main__":
    constraints = PromptVariantConstraints(
        require_concise=True,
        require_citations=True,
        tool_usage="minimal",
    )
    dev_tasks = [
        {"task_id": "ra_001", "instruction": "Summarize sources"},
        {"task_id": "ra_002", "instruction": "Compare claims"},
    ]

    result = sweep_prompt_variants_on_dev_tasks(
        "You are a helpful research assistant.",
        dev_tasks=dev_tasks,
        score_task_fn=lambda prompt, _task: 1.0 if "Cite sources" in prompt else 0.8,
        constraints=constraints,
    )
    for outcome in result.outcomes:
        print(outcome.candidate_id, outcome.score)
