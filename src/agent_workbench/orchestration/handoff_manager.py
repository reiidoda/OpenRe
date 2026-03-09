"""Handoff manager placeholder."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class HandoffManager:
    def route(self, task_modality: str) -> str:
        if task_modality == "image":
            return "multimodal_agent"
        if task_modality in {"browser", "computer"}:
            return "browser_agent"
        return "research_agent"
