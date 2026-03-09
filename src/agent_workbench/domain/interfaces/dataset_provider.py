"""Dataset provider interface."""

from __future__ import annotations

from typing import Protocol

from agent_workbench.domain.entities.task import TaskSpec


class DatasetProvider(Protocol):
    def load_tasks(self, dataset_path: str) -> list[TaskSpec]:
        """Load tasks from a dataset path."""
