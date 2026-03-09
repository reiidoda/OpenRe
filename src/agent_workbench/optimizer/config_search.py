"""Config search strategy."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class WeightedObjectiveSearch:
    quality_w: float = 0.50
    trace_w: float = 0.20
    safety_w: float = 0.10
    latency_w: float = 0.10
    cost_w: float = 0.10

    def score(self, candidate: dict[str, float]) -> float:
        return (
            self.quality_w * candidate.get("task_quality", 0.0)
            + self.trace_w * candidate.get("trace_quality", 0.0)
            + self.safety_w * candidate.get("safety_compliance", 0.0)
            + self.latency_w * candidate.get("latency_score", 0.0)
            + self.cost_w * candidate.get("cost_efficiency", 0.0)
        )

    def optimize(self, candidates: list[dict[str, float]]) -> dict[str, float]:
        if not candidates:
            return {}
        return max(candidates, key=self.score)
