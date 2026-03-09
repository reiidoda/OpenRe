"""Optimizer service."""

from __future__ import annotations

from dataclasses import dataclass

from agent_workbench.domain.interfaces.optimizer import Optimizer


@dataclass(slots=True)
class OptimizeService:
    optimizer: Optimizer

    def choose(self, candidates: list[dict[str, object]]) -> dict[str, object]:
        return self.optimizer.optimize(candidates)
