"""Rubric grader placeholder."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agent_workbench.domain.entities.evaluation import EvaluationResult


def _coerce_terms(value: object) -> list[str]:
    if isinstance(value, str):
        term = value.strip().lower()
        return [term] if term else []
    if isinstance(value, list):
        terms: list[str] = []
        for item in value:
            if isinstance(item, str):
                term = item.strip().lower()
                if term:
                    terms.append(term)
        return terms
    return []


def _clamp_score(score: float) -> float:
    if score < 0.0:
        return 0.0
    if score > 1.0:
        return 1.0
    return score


@dataclass(slots=True)
class RubricGrader:
    name: str = "rubric_grade"
    criteria_weights: dict[str, float] = field(default_factory=dict)

    def evaluate(self, output: str, expected: dict[str, object]) -> EvaluationResult:
        criteria = self._resolve_criteria(expected)
        if not criteria:
            return EvaluationResult(
                evaluator_name=self.name,
                metric_name="rubric",
                score=0.0,
                rationale="No rubric criteria were provided.",
                labels=["rubric:no_criteria"],
            )

        output_text = output.lower()
        weighted_score = 0.0
        total_weight = 0.0
        criterion_reasons: list[str] = []

        for criterion in criteria:
            name = criterion["name"]
            required_terms = criterion["required_terms"]
            mode = criterion["mode"]
            weight = criterion["weight"]

            criterion_score = self._criterion_score(
                output_text=output_text,
                required_terms=required_terms,
                mode=mode,
            )
            weighted_score += criterion_score * weight
            total_weight += weight
            criterion_reasons.append(
                f"{name}={criterion_score:.2f} (w={weight:.2f}, mode={mode}, terms={required_terms})"
            )

        final_score = _clamp_score(weighted_score / total_weight) if total_weight > 0 else 0.0
        labels = ["rubric:pass"] if final_score >= 0.6 else ["rubric:fail"]
        return EvaluationResult(
            evaluator_name=self.name,
            metric_name="rubric",
            score=final_score,
            rationale="Deterministic weighted rubric scoring. " + "; ".join(criterion_reasons),
            labels=labels,
        )

    def _resolve_criteria(self, expected: dict[str, object]) -> list[dict[str, Any]]:
        rubric = expected.get("rubric")
        if not isinstance(rubric, dict):
            return []
        raw_criteria = rubric.get("criteria")
        if not isinstance(raw_criteria, list):
            return []

        criteria: list[dict[str, Any]] = []
        for raw in raw_criteria:
            if not isinstance(raw, dict):
                continue
            name_value = raw.get("name")
            if not isinstance(name_value, str):
                continue
            name = name_value.strip()
            if not name:
                continue

            terms = _coerce_terms(raw.get("required_terms"))
            if not terms:
                continue

            mode_raw = raw.get("mode")
            mode = "all" if isinstance(mode_raw, str) and mode_raw.lower() == "all" else "any"

            weight = self._resolve_weight(name=name, raw_weight=raw.get("weight"))
            criteria.append(
                {
                    "name": name,
                    "required_terms": terms,
                    "mode": mode,
                    "weight": weight,
                }
            )

        if not criteria:
            return []

        total_weight = sum(float(item["weight"]) for item in criteria)
        if total_weight <= 0:
            equal_weight = 1.0 / len(criteria)
            for item in criteria:
                item["weight"] = equal_weight
            return criteria

        for item in criteria:
            item["weight"] = float(item["weight"]) / total_weight
        return criteria

    def _resolve_weight(self, *, name: str, raw_weight: object) -> float:
        if isinstance(raw_weight, (int, float)) and float(raw_weight) > 0:
            return float(raw_weight)
        configured = self.criteria_weights.get(name)
        if isinstance(configured, (int, float)) and float(configured) > 0:
            return float(configured)
        return 1.0

    @staticmethod
    def _criterion_score(*, output_text: str, required_terms: list[str], mode: str) -> float:
        match_count = sum(1 for term in required_terms if term in output_text)
        total_terms = len(required_terms)
        if total_terms == 0:
            return 0.0

        if mode == "all":
            return _clamp_score(match_count / total_terms)
        return 1.0 if match_count > 0 else 0.0
