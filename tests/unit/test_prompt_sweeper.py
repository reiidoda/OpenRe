from __future__ import annotations

from agent_workbench.optimizer.prompt_sweeper import (
    PromptVariantConstraints,
    generate_variant_candidates,
    generate_variants,
    sweep_prompt_variants,
    sweep_prompt_variants_on_dev_tasks,
)


def test_generate_variant_candidates_accepts_constraints_and_keeps_order() -> None:
    constraints = PromptVariantConstraints(
        require_concise=True,
        require_citations=True,
        tool_usage="minimal",
        extra_directives=["Use bullet points.", "Cite sources for factual claims."],
        max_variants=8,
    )

    candidates = generate_variant_candidates(
        "You are a helpful research assistant.",
        constraints=constraints,
    )

    assert [candidate.candidate_id for candidate in candidates] == [
        "prompt_000",
        "prompt_001",
        "prompt_002",
        "prompt_003",
        "prompt_004",
        "prompt_005",
    ]
    assert candidates[0].prompt == "You are a helpful research assistant."
    assert candidates[1].directives == ["Keep the response concise and scannable."]
    assert candidates[2].directives == ["Cite sources for factual claims."]
    assert candidates[3].directives == ["Use tools only when necessary."]
    assert candidates[4].directives == ["Use bullet points."]
    assert candidates[5].directives == [
        "Keep the response concise and scannable.",
        "Cite sources for factual claims.",
        "Use tools only when necessary.",
        "Use bullet points.",
    ]

    # Compatibility API still returns a plain list of prompt strings.
    prompt_list = generate_variants(
        "You are a helpful research assistant.", constraints=constraints
    )
    assert prompt_list == [candidate.prompt for candidate in candidates]


def test_sweep_prompt_variants_records_candidate_ids_and_scores() -> None:
    result = sweep_prompt_variants(
        "Base prompt.",
        score_fn=lambda prompt: float(len(prompt)),
        constraints=PromptVariantConstraints(require_concise=True),
    )

    assert [entry.candidate_id for entry in result.outcomes] == ["prompt_000", "prompt_001"]
    assert result.ranking == ["prompt_001", "prompt_000"]
    assert result.best_candidate_id == "prompt_001"
    assert result.best_score == result.outcomes[1].score


def test_sweep_prompt_variants_on_dev_tasks_is_deterministic_for_ties() -> None:
    tasks = [
        {"task_id": "ra_001", "instruction": "Task A"},
        {"task_id": "ra_002", "instruction": "Task B"},
    ]
    constraints = PromptVariantConstraints(require_concise=True, require_citations=True)

    first = sweep_prompt_variants_on_dev_tasks(
        "Base prompt.",
        dev_tasks=tasks,
        score_task_fn=lambda _prompt, _task: 0.5,
        constraints=constraints,
    )
    second = sweep_prompt_variants_on_dev_tasks(
        "Base prompt.",
        dev_tasks=tasks,
        score_task_fn=lambda _prompt, _task: 0.5,
        constraints=constraints,
    )

    expected_candidate_ids = [entry.candidate_id for entry in first.outcomes]
    assert first.ranking == expected_candidate_ids
    assert second.ranking == expected_candidate_ids
    assert first.best_candidate_id == expected_candidate_ids[0]
    assert second.best_candidate_id == expected_candidate_ids[0]
    assert first.outcomes[0].task_scores == {"ra_001": 0.5, "ra_002": 0.5}
