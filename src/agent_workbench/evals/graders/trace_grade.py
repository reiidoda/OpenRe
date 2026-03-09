"""Trace grader placeholder."""

from __future__ import annotations

from dataclasses import dataclass

from agent_workbench.domain.entities.evaluation import EvaluationResult


@dataclass(slots=True)
class TraceGrader:
    name: str = "trace_grade"

    def evaluate(self, output: str, expected: dict[str, object]) -> EvaluationResult:
        _ = (output, expected)
        return EvaluationResult(
            evaluator_name=self.name,
            metric_name="trace_quality",
            score=0.5,
            rationale="Trace grading placeholder.",
            labels=["placeholder"],
        )
