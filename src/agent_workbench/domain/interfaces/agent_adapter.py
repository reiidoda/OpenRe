"""Agent adapter interface."""

from __future__ import annotations

from typing import Protocol

from agent_workbench.domain.entities.task import TaskSpec


class AgentAdapter(Protocol):
    def run_task(self, task: TaskSpec, config_path: str) -> str:
        """Run task with given config and return final output."""
