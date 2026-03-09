"""Evaluation service."""

from __future__ import annotations

from dataclasses import dataclass

from agent_workbench.domain.entities.evaluation import EvaluationResult
from agent_workbench.domain.interfaces.evaluator import Evaluator


@dataclass(slots=True)
class EvalService:
    evaluators: list[Evaluator]

    def evaluate(self, output: str, expected: dict[str, object]) -> list[EvaluationResult]:
        return [
            evaluator.evaluate(output=output, expected=expected) for evaluator in self.evaluators
        ]
