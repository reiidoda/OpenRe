"""Rubric grader placeholder."""

from __future__ import annotations

from dataclasses import dataclass

from agent_workbench.domain.entities.evaluation import EvaluationResult


@dataclass(slots=True)
class RubricGrader:
    name: str = "rubric_grade"

    def evaluate(self, output: str, expected: dict[str, object]) -> EvaluationResult:
        _ = (output, expected)
        return EvaluationResult(
            evaluator_name=self.name,
            metric_name="rubric",
            score=0.5,
            rationale="Scaffold placeholder rubric score.",
            labels=["placeholder"],
        )
