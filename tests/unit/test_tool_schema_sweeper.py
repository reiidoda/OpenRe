from __future__ import annotations

from agent_workbench.domain.value_objects.risk_level import RiskLevel
from agent_workbench.optimizer.tool_schema_sweeper import (
    ToolSchemaSearchSpace,
    generate_schema_variant_candidates,
    generate_schema_variants,
    sweep_tool_schema_variants,
)


def test_generate_schema_variants_mutates_fields_from_search_space() -> None:
    base_schema = {
        "description": "Search sources",
        "strict": False,
        "parameters": {"additionalProperties": True},
    }
    search_space = ToolSchemaSearchSpace(
        field_values={
            "strict": [False, True],
            "description": ["Search sources", "Search sources and verify citations"],
            "parameters.additionalProperties": [True, False],
        },
        include_base=True,
        max_variants=8,
    )

    candidates = generate_schema_variant_candidates(base_schema, search_space=search_space)
    schemas = generate_schema_variants(base_schema, search_space=search_space)

    assert candidates[0].variant_id == "schema_000"
    assert candidates[0].mutations == {}
    assert any(candidate.mutations.get("strict") is True for candidate in candidates)
    assert any(
        candidate.mutations.get("parameters.additionalProperties") is False
        for candidate in candidates
    )
    assert any(
        candidate.mutations.get("description") == "Search sources and verify citations"
        for candidate in candidates
    )
    assert schemas[0]["strict"] is False


def test_sweep_tool_schema_variants_records_variant_trace_mapping() -> None:
    base_schema = {"description": "Summarize a report", "strict": False}
    result = sweep_tool_schema_variants(
        base_schema,
        run_candidate=lambda variant_id, _schema: (0.8, f"trace-{variant_id}"),
        search_space=ToolSchemaSearchSpace(field_values={"strict": [False, True]}),
    )

    executed_outcomes = [outcome for outcome in result.outcomes if outcome.executed]
    assert executed_outcomes
    assert all(outcome.trace_id is not None for outcome in executed_outcomes)
    assert all(outcome.trace_id == f"trace-{outcome.variant_id}" for outcome in executed_outcomes)
    assert result.ranking == sorted(result.ranking)


def test_safety_checks_run_before_candidate_execution() -> None:
    base_schema = {"description": "Delete user account"}
    execution_count = 0

    def run_candidate(_variant_id: str, _schema: dict[str, object]) -> float:
        nonlocal execution_count
        execution_count += 1
        return 1.0

    result = sweep_tool_schema_variants(
        base_schema,
        run_candidate=run_candidate,
        search_space=ToolSchemaSearchSpace(field_values={"strict": [True]}),
    )

    assert execution_count == 0
    assert result.best_variant_id is None
    assert result.ranking == []
    assert result.outcomes[0].executed is False
    assert result.outcomes[0].risk_level == RiskLevel.CRITICAL
    assert result.outcomes[0].decision.allowed is False
