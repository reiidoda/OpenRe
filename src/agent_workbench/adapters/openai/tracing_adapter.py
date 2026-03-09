"""OpenAI tracing adapter placeholder."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TracingAdapter:
    def describe(self) -> str:
        return "Tracing adapter placeholder"
