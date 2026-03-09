"""Evaluation harness."""

from __future__ import annotations

from dataclasses import dataclass

from agent_workbench.domain.entities.evaluation import EvaluationResult
from agent_workbench.domain.interfaces.evaluator import Evaluator


@dataclass(slots=True)
class EvalHarness:
    evaluators: list[Evaluator]

    def run(self, output: str, expected: dict[str, object]) -> list[EvaluationResult]:
        return [e.evaluate(output, expected) for e in self.evaluators]
