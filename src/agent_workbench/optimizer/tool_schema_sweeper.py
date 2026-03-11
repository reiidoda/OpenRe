"""Tool schema sweeper with deterministic mutation and safety prechecks."""

from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass
from dataclasses import field
from itertools import product
import json

from agent_workbench.domain.value_objects.risk_level import RiskLevel
from agent_workbench.safety.policy_engine import PolicyDecision
from agent_workbench.safety.policy_engine import PolicyEngine
from agent_workbench.safety.risk_classifier import classify_action

ToolSchemaRunFn = Callable[[str, dict[str, object]], float | tuple[float, str | None]]


@dataclass(slots=True)
class ToolSchemaSearchSpace:
    field_values: dict[str, list[object]] = field(default_factory=lambda: {"strict": [True]})
    max_variants: int = 12
    include_base: bool = True


@dataclass(slots=True)
class ToolSchemaVariant:
    variant_id: str
    schema: dict[str, object]
    mutations: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class ToolSchemaSweepOutcome:
    variant_id: str
    score: float | None
    trace_id: str | None
    executed: bool
    risk_level: RiskLevel
    decision: PolicyDecision
    mutations: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class ToolSchemaSweepResult:
    outcomes: list[ToolSchemaSweepOutcome]
    ranking: list[str]
    best_variant_id: str | None
    best_score: float | None


def _sanitize_base_schema(base_schema: dict[str, object]) -> dict[str, object]:
    if not base_schema:
        raise ValueError("base schema must be non-empty.")
    return deepcopy(base_schema)


def _normalize_search_space(search_space: ToolSchemaSearchSpace | None) -> ToolSchemaSearchSpace:
    active = search_space or ToolSchemaSearchSpace()
    if active.max_variants < 1:
        raise ValueError("max_variants must be >= 1.")
    if not active.field_values:
        raise ValueError("field_values must include at least one path.")
    for path, values in active.field_values.items():
        if not path.strip():
            raise ValueError("field path keys must be non-empty.")
        if not isinstance(values, list) or not values:
            raise ValueError(f"field_values['{path}'] must be a non-empty list.")
    return active


def _fingerprint(value: object) -> str:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    except TypeError:
        return repr(value)


def _dedupe_values(values: list[object]) -> list[object]:
    deduped: list[object] = []
    seen: set[str] = set()
    for value in values:
        marker = _fingerprint(value)
        if marker in seen:
            continue
        seen.add(marker)
        deduped.append(deepcopy(value))
    return deduped


def _get_path(source: dict[str, object], field_path: str) -> object:
    current: object = source
    for part in field_path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _set_path(target: dict[str, object], field_path: str, value: object) -> None:
    parts = field_path.split(".")
    current = target
    for part in parts[:-1]:
        existing = current.get(part)
        if not isinstance(existing, dict):
            existing = {}
            current[part] = existing
        current = existing
    current[parts[-1]] = value


def generate_schema_variant_candidates(
    base_schema: dict[str, object],
    search_space: ToolSchemaSearchSpace | None = None,
) -> list[ToolSchemaVariant]:
    normalized_base = _sanitize_base_schema(base_schema)
    active_space = _normalize_search_space(search_space)

    paths = sorted(active_space.field_values.keys())
    values_by_path = [_dedupe_values(active_space.field_values[path]) for path in paths]

    variants: list[ToolSchemaVariant] = []
    seen_schemas: set[str] = set()

    def append_variant(schema: dict[str, object], mutations: dict[str, object]) -> None:
        if len(variants) >= active_space.max_variants:
            return
        marker = _fingerprint(schema)
        if marker in seen_schemas:
            return
        seen_schemas.add(marker)
        variants.append(
            ToolSchemaVariant(
                variant_id=f"schema_{len(variants):03d}",
                schema=schema,
                mutations=mutations,
            )
        )

    if active_space.include_base:
        append_variant(deepcopy(normalized_base), {})

    for combination in product(*values_by_path):
        schema = deepcopy(normalized_base)
        mutations: dict[str, object] = {}
        for path, value in zip(paths, combination):
            _set_path(schema, path, deepcopy(value))
            if _get_path(normalized_base, path) != value:
                mutations[path] = deepcopy(value)
        append_variant(schema, mutations)
        if len(variants) >= active_space.max_variants:
            break

    return variants


def generate_schema_variants(
    base: dict[str, object],
    search_space: ToolSchemaSearchSpace | None = None,
) -> list[dict[str, object]]:
    """Backward-compatible schema-only variant list API."""
    return [
        candidate.schema for candidate in generate_schema_variant_candidates(base, search_space)
    ]


def _default_policy_engine() -> PolicyEngine:
    return PolicyEngine(
        require_approval_for=[RiskLevel.HIGH, RiskLevel.CRITICAL],
        deny_levels=[RiskLevel.CRITICAL],
    )


def _schema_action_text(schema: dict[str, object]) -> str:
    parts: list[str] = []
    for key in ("name", "description", "title"):
        value = schema.get(key)
        if isinstance(value, str) and value.strip():
            parts.append(value.strip())
    parameters = schema.get("parameters")
    if isinstance(parameters, dict):
        properties = parameters.get("properties")
        if isinstance(properties, dict):
            parts.extend(
                key.strip() for key in properties.keys() if isinstance(key, str) and key.strip()
            )
    return " ".join(parts)


def _rank_outcomes(outcomes: list[ToolSchemaSweepOutcome]) -> list[ToolSchemaSweepOutcome]:
    executed: list[ToolSchemaSweepOutcome] = []
    for outcome in outcomes:
        if outcome.executed and outcome.score is not None:
            executed.append(outcome)
    return sorted(
        executed,
        key=lambda outcome: (-(outcome.score or 0.0), outcome.variant_id),
    )


def sweep_tool_schema_variants(
    base_schema: dict[str, object],
    run_candidate: ToolSchemaRunFn,
    *,
    search_space: ToolSchemaSearchSpace | None = None,
    policy_engine: PolicyEngine | None = None,
    allow_approval_required: bool = False,
) -> ToolSchemaSweepResult:
    variants = generate_schema_variant_candidates(base_schema, search_space)
    active_policy = policy_engine or _default_policy_engine()
    outcomes: list[ToolSchemaSweepOutcome] = []

    for variant in variants:
        action_text = _schema_action_text(variant.schema)
        risk_level = classify_action(action_text)
        decision = active_policy.evaluate(risk_level)
        can_execute = decision.allowed and (
            allow_approval_required or not decision.requires_approval
        )
        if not can_execute:
            outcomes.append(
                ToolSchemaSweepOutcome(
                    variant_id=variant.variant_id,
                    score=None,
                    trace_id=None,
                    executed=False,
                    risk_level=risk_level,
                    decision=decision,
                    mutations=variant.mutations,
                )
            )
            continue

        run_result = run_candidate(variant.variant_id, deepcopy(variant.schema))
        if isinstance(run_result, tuple):
            score_raw, trace_id_raw = run_result
            trace_id = trace_id_raw
        else:
            score_raw = run_result
            trace_id = None
        score = round(float(score_raw), 6)
        trace = trace_id or f"schema_variant:{variant.variant_id}"
        outcomes.append(
            ToolSchemaSweepOutcome(
                variant_id=variant.variant_id,
                score=score,
                trace_id=trace,
                executed=True,
                risk_level=risk_level,
                decision=decision,
                mutations=variant.mutations,
            )
        )

    ranked = _rank_outcomes(outcomes)
    return ToolSchemaSweepResult(
        outcomes=outcomes,
        ranking=[item.variant_id for item in ranked],
        best_variant_id=ranked[0].variant_id if ranked else None,
        best_score=ranked[0].score if ranked else None,
    )
