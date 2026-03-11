from agent_workbench.optimizer.tool_schema_sweeper import (
    ToolSchemaSearchSpace,
    sweep_tool_schema_variants,
)


if __name__ == "__main__":
    base_schema = {
        "name": "web_search",
        "description": "Search sources and summarize findings.",
        "strict": False,
        "parameters": {
            "additionalProperties": True,
            "properties": {"query": {"type": "string"}},
        },
    }
    search_space = ToolSchemaSearchSpace(
        field_values={
            "strict": [False, True],
            "description": [
                "Search sources and summarize findings.",
                "Search sources, verify findings, and include citations.",
            ],
            "parameters.additionalProperties": [True, False],
        },
        max_variants=6,
    )
    result = sweep_tool_schema_variants(
        base_schema,
        run_candidate=lambda variant_id, schema: (
            1.0 if schema.get("strict") else 0.7,
            f"trace-{variant_id}",
        ),
        search_space=search_space,
    )
    for outcome in result.outcomes:
        print(outcome.variant_id, outcome.executed, outcome.score, outcome.trace_id)
