"""Prompt sweeper for deterministic prompt-variant search."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from typing import Literal


ToolUsageMode = Literal["balanced", "minimal", "aggressive"]
PromptScoreFn = Callable[[str], float]
TaskScoreFn = Callable[[str, dict[str, object]], float]


@dataclass(slots=True)
class PromptVariantConstraints:
    require_citations: bool = False
    require_concise: bool = False
    tool_usage: ToolUsageMode = "balanced"
    extra_directives: list[str] = field(default_factory=list)
    max_variants: int = 8


@dataclass(slots=True)
class PromptVariant:
    candidate_id: str
    prompt: str
    directives: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PromptCandidateOutcome:
    candidate_id: str
    prompt: str
    score: float
    task_scores: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class PromptSweepResult:
    base_prompt: str
    constraints: PromptVariantConstraints
    outcomes: list[PromptCandidateOutcome] = field(default_factory=list)
    ranking: list[str] = field(default_factory=list)
    best_candidate_id: str | None = None
    best_score: float | None = None


def _sanitize_prompt(base_prompt: str) -> str:
    normalized = base_prompt.strip()
    if not normalized:
        raise ValueError("base_prompt must be non-empty.")
    return normalized


def _normalize_constraints(
    constraints: PromptVariantConstraints | None,
) -> PromptVariantConstraints:
    active = constraints or PromptVariantConstraints()
    if active.max_variants < 1:
        raise ValueError("max_variants must be >= 1.")
    return active


def _clean_directive(raw: str) -> str:
    return " ".join(raw.split()).strip()


def _append_unique_directive(directives: list[str], directive: str) -> None:
    clean = _clean_directive(directive)
    if clean and clean not in directives:
        directives.append(clean)


def _build_directive_pool(constraints: PromptVariantConstraints) -> list[str]:
    directives: list[str] = []
    if constraints.require_concise:
        _append_unique_directive(directives, "Keep the response concise and scannable.")
    if constraints.require_citations:
        _append_unique_directive(directives, "Cite sources for factual claims.")
    if constraints.tool_usage == "minimal":
        _append_unique_directive(directives, "Use tools only when necessary.")
    elif constraints.tool_usage == "aggressive":
        _append_unique_directive(directives, "Use tools proactively to verify key claims.")
    for extra in constraints.extra_directives:
        _append_unique_directive(directives, extra)
    return directives


def generate_variant_candidates(
    base_prompt: str,
    constraints: PromptVariantConstraints | None = None,
) -> list[PromptVariant]:
    normalized_prompt = _sanitize_prompt(base_prompt)
    active_constraints = _normalize_constraints(constraints)
    directives = _build_directive_pool(active_constraints)

    prompts: list[PromptVariant] = [
        PromptVariant(candidate_id="prompt_000", prompt=normalized_prompt, directives=[])
    ]

    for directive in directives:
        prompts.append(
            PromptVariant(
                candidate_id=f"prompt_{len(prompts):03d}",
                prompt=f"{normalized_prompt}\n{directive}",
                directives=[directive],
            )
        )

    if len(directives) > 1:
        prompts.append(
            PromptVariant(
                candidate_id=f"prompt_{len(prompts):03d}",
                prompt=f"{normalized_prompt}\n" + "\n".join(directives),
                directives=list(directives),
            )
        )

    return prompts[: active_constraints.max_variants]


def _rank_outcomes(outcomes: list[PromptCandidateOutcome]) -> list[PromptCandidateOutcome]:
    return sorted(outcomes, key=lambda outcome: (-outcome.score, outcome.candidate_id))


def _average(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def sweep_prompt_variants(
    base_prompt: str,
    score_fn: PromptScoreFn,
    constraints: PromptVariantConstraints | None = None,
) -> PromptSweepResult:
    candidates = generate_variant_candidates(base_prompt=base_prompt, constraints=constraints)
    outcomes: list[PromptCandidateOutcome] = []
    for candidate in candidates:
        score = float(score_fn(candidate.prompt))
        outcomes.append(
            PromptCandidateOutcome(
                candidate_id=candidate.candidate_id,
                prompt=candidate.prompt,
                score=round(score, 6),
            )
        )
    ranked = _rank_outcomes(outcomes)
    return PromptSweepResult(
        base_prompt=_sanitize_prompt(base_prompt),
        constraints=_normalize_constraints(constraints),
        outcomes=outcomes,
        ranking=[entry.candidate_id for entry in ranked],
        best_candidate_id=ranked[0].candidate_id if ranked else None,
        best_score=ranked[0].score if ranked else None,
    )


def sweep_prompt_variants_on_dev_tasks(
    base_prompt: str,
    dev_tasks: list[dict[str, object]],
    score_task_fn: TaskScoreFn,
    constraints: PromptVariantConstraints | None = None,
) -> PromptSweepResult:
    candidates = generate_variant_candidates(base_prompt=base_prompt, constraints=constraints)
    outcomes: list[PromptCandidateOutcome] = []
    for candidate in candidates:
        task_scores: dict[str, float] = {}
        for index, task in enumerate(dev_tasks):
            task_id_raw = task.get("task_id")
            if isinstance(task_id_raw, str) and task_id_raw.strip():
                task_id = task_id_raw.strip()
            else:
                task_id = f"task_{index:03d}"
            task_scores[task_id] = round(float(score_task_fn(candidate.prompt, task)), 6)
        aggregate_score = round(_average(list(task_scores.values())), 6)
        outcomes.append(
            PromptCandidateOutcome(
                candidate_id=candidate.candidate_id,
                prompt=candidate.prompt,
                score=aggregate_score,
                task_scores=task_scores,
            )
        )

    ranked = _rank_outcomes(outcomes)
    return PromptSweepResult(
        base_prompt=_sanitize_prompt(base_prompt),
        constraints=_normalize_constraints(constraints),
        outcomes=outcomes,
        ranking=[entry.candidate_id for entry in ranked],
        best_candidate_id=ranked[0].candidate_id if ranked else None,
        best_score=ranked[0].score if ranked else None,
    )


def generate_variants(
    base_prompt: str,
    constraints: PromptVariantConstraints | None = None,
) -> list[str]:
    """Backward-compatible prompt list API."""
    return [candidate.prompt for candidate in generate_variant_candidates(base_prompt, constraints)]
