"""Token and cost accounting value object."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TokenCost:
    input_tokens: int = 0
    output_tokens: int = 0
    usd: float = 0.0

    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens
