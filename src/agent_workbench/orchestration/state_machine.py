"""Task run state machine."""

from __future__ import annotations

from dataclasses import dataclass

from agent_workbench.domain.entities.run import TaskRun, TaskRunStatus


@dataclass(slots=True)
class TaskRunStateMachine:
    def transition(self, task_run: TaskRun, target: TaskRunStatus) -> None:
        allowed = {
            TaskRunStatus.CREATED: {TaskRunStatus.RUNNING},
            TaskRunStatus.RUNNING: {
                TaskRunStatus.WAITING_APPROVAL,
                TaskRunStatus.EVALUATING,
                TaskRunStatus.FAILED,
            },
            TaskRunStatus.WAITING_APPROVAL: {TaskRunStatus.RESUMED, TaskRunStatus.REJECTED},
            TaskRunStatus.RESUMED: {TaskRunStatus.EVALUATING, TaskRunStatus.FAILED},
            TaskRunStatus.EVALUATING: {TaskRunStatus.COMPLETED, TaskRunStatus.FAILED},
        }
        if target not in allowed.get(task_run.status, set()):
            raise ValueError(f"Invalid transition {task_run.status} -> {target}")
        task_run.status = target
