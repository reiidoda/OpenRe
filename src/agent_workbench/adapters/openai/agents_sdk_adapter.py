"""OpenAI Agents SDK adapter placeholder."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AgentsSdkAdapter:
    def describe(self) -> str:
        return "Agents SDK adapter placeholder"
