"""Benchmark metric computations."""

from __future__ import annotations


def average(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def weighted_score(
    *,
    output_quality: float,
    trace_quality: float,
    output_weight: float = 0.8,
    trace_weight: float = 0.2,
) -> float:
    output_component = max(0.0, output_weight)
    trace_component = max(0.0, trace_weight)
    total_weight = output_component + trace_component
    if total_weight <= 0:
        return 0.0
    score = (
        output_quality * output_component + trace_quality * trace_component
    ) / total_weight
    if score < 0.0:
        return 0.0
    if score > 1.0:
        return 1.0
    return score
