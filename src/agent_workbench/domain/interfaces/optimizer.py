"""Optimizer interface."""

from __future__ import annotations

from typing import Protocol


class Optimizer(Protocol):
    def optimize(self, candidates: list[dict[str, object]]) -> dict[str, object]:
        """Return the best candidate config."""
