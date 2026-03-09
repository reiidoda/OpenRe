"""Pairwise comparison grader placeholder."""

from __future__ import annotations

from dataclasses import dataclass

from agent_workbench.domain.entities.evaluation import EvaluationResult


@dataclass(slots=True)
class PairwiseCompareGrader:
    name: str = "pairwise_compare"

    def evaluate(self, output: str, expected: dict[str, object]) -> EvaluationResult:
        _ = (output, expected)
        return EvaluationResult(
            evaluator_name=self.name,
            metric_name="pairwise",
            score=0.5,
            rationale="Pairwise grading placeholder.",
            labels=["placeholder"],
        )
