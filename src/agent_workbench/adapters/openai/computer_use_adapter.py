"""OpenAI computer-use adapter placeholder."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ComputerUseAdapter:
    def describe(self) -> str:
        return "Computer-use adapter placeholder"
