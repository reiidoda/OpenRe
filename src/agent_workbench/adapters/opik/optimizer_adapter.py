"""Opik optimizer adapter placeholder."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class OpikOptimizerAdapter:
    enabled: bool = False

    def suggest(self) -> dict[str, object]:
        return {"enabled": self.enabled}
