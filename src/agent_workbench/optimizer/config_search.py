"""Weighted objective rankers for optimization candidate search."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
import json
from typing import Mapping


DEFAULT_OBJECTIVE_WEIGHTS: dict[str, float] = {
    "task_quality": 0.50,
    "trace_quality": 0.20,
    "safety_compliance": 0.10,
    "latency_score": 0.10,
    "cost_efficiency": 0.10,
}


@dataclass(slots=True)
class CandidateRanking:
    candidate_id: str
    score: float
    candidate: dict[str, object]


def _to_float(value: object) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0


def _candidate_id(candidate: dict[str, object]) -> str:
    for key in ("candidate_id", "id", "config_id", "name"):
        raw = candidate.get(key)
        if isinstance(raw, str) and raw.strip():
            return raw.strip()
    try:
        return json.dumps(candidate, sort_keys=True, default=str)
    except TypeError:
        return repr(candidate)


def _normalize_weights(weights: Mapping[str, float], normalize: bool) -> dict[str, float]:
    cleaned: dict[str, float] = {}
    for metric, raw_weight in weights.items():
        metric_name = metric.strip()
        if not metric_name:
            continue
        weight = float(raw_weight)
        if weight < 0:
            raise ValueError(f"Weight for '{metric_name}' must be >= 0.")
        cleaned[metric_name] = weight
    if not cleaned:
        raise ValueError("At least one objective weight is required.")

    total = sum(cleaned.values())
    if total <= 0:
        raise ValueError("At least one objective weight must be > 0.")

    if not normalize:
        return cleaned
    return {metric: weight / total for metric, weight in cleaned.items()}


@dataclass(slots=True)
class WeightedObjectiveRanker:
    objective_weights: dict[str, float] = field(
        default_factory=lambda: dict(DEFAULT_OBJECTIVE_WEIGHTS)
    )
    normalize_weights: bool = True

    @classmethod
    def from_config(cls, config: Mapping[str, object]) -> WeightedObjectiveRanker:
        raw_weights = config.get("weights")
        if isinstance(raw_weights, Mapping):
            converted: dict[str, float] = {}
            for metric, weight in raw_weights.items():
                if isinstance(metric, str):
                    converted[metric] = _to_float(weight)
        else:
            converted = dict(DEFAULT_OBJECTIVE_WEIGHTS)

        normalize = config.get("normalize_weights", True)
        return cls(
            objective_weights=converted,
            normalize_weights=bool(normalize),
        )

    def resolved_weights(self) -> dict[str, float]:
        return _normalize_weights(self.objective_weights, self.normalize_weights)

    def score_breakdown(self, candidate: dict[str, object]) -> dict[str, float]:
        weights = self.resolved_weights()
        return {
            metric: round(weight * _to_float(candidate.get(metric)), 6)
            for metric, weight in weights.items()
        }

    def score(self, candidate: dict[str, object]) -> float:
        breakdown = self.score_breakdown(candidate)
        return round(sum(breakdown.values()), 6)

    def rank_with_scores(self, candidates: list[dict[str, object]]) -> list[CandidateRanking]:
        rankings = [
            CandidateRanking(
                candidate_id=_candidate_id(candidate),
                score=self.score(candidate),
                candidate=candidate,
            )
            for candidate in candidates
        ]
        return sorted(rankings, key=lambda ranking: (-ranking.score, ranking.candidate_id))

    def rank(self, candidates: list[dict[str, object]]) -> list[dict[str, object]]:
        return [ranking.candidate for ranking in self.rank_with_scores(candidates)]

    def optimize(self, candidates: list[dict[str, object]]) -> dict[str, object]:
        if not candidates:
            return {}
        return self.rank(candidates)[0]


@dataclass(slots=True)
class WeightedObjectiveSearch(WeightedObjectiveRanker):
    quality_w: float = 0.50
    trace_w: float = 0.20
    safety_w: float = 0.10
    latency_w: float = 0.10
    cost_w: float = 0.10
    normalize_legacy_weights: bool = True

    def resolved_weights(self) -> dict[str, float]:
        legacy = {
            "task_quality": self.quality_w,
            "trace_quality": self.trace_w,
            "safety_compliance": self.safety_w,
            "latency_score": self.latency_w,
            "cost_efficiency": self.cost_w,
        }
        if self.objective_weights != DEFAULT_OBJECTIVE_WEIGHTS:
            legacy = self.objective_weights
        return _normalize_weights(legacy, self.normalize_legacy_weights)
