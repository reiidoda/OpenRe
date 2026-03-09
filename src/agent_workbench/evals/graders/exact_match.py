"""Exact match grader."""

from __future__ import annotations

from dataclasses import dataclass

from agent_workbench.domain.entities.evaluation import EvaluationResult


@dataclass(slots=True)
class ExactMatchGrader:
    name: str = "exact_match"

    def evaluate(self, output: str, expected: dict[str, object]) -> EvaluationResult:
        expected_text = str(expected.get("target", "")).strip()
        score = 1.0 if output.strip() == expected_text else 0.0
        return EvaluationResult(
            evaluator_name=self.name,
            metric_name="exact_match",
            score=score,
            rationale="Exact text comparison.",
            labels=[],
        )
