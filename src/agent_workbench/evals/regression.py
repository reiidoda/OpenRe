"""Regression gate checks."""

from __future__ import annotations


def violates_threshold(current: float, baseline: float, max_drop: float = 0.02) -> bool:
    return current < (baseline - max_drop)
