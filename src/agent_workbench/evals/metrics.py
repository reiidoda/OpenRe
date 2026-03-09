"""Benchmark metric computations."""

from __future__ import annotations


def average(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)
