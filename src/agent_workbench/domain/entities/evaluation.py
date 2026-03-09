"""Evaluation result entity."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class EvaluationResult:
    evaluator_name: str
    metric_name: str
    score: float
    rationale: str
    labels: list[str] = field(default_factory=list)
