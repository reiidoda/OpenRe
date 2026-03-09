"""Score value object."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Score:
    value: float
    max_value: float = 1.0

    def normalized(self) -> float:
        if self.max_value <= 0:
            return 0.0
        return max(0.0, min(1.0, self.value / self.max_value))
