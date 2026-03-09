"""OpenAI Responses adapter placeholder."""

from __future__ import annotations

from dataclasses import dataclass

from agent_workbench.domain.entities.task import TaskSpec


@dataclass(slots=True)
class ResponsesAdapter:
    """Placeholder adapter for future OpenAI Responses integration."""

    def run_task(self, task: TaskSpec, config_path: str) -> str:
        return f"[responses_adapter] task={task.task_id} config={config_path}"
