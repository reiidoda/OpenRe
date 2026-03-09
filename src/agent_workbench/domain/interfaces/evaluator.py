"""Evaluator interface."""

from __future__ import annotations

from typing import Protocol

from agent_workbench.domain.entities.evaluation import EvaluationResult


class Evaluator(Protocol):
    name: str

    def evaluate(self, output: str, expected: dict[str, object]) -> EvaluationResult:
        """Evaluate output against expected data."""
