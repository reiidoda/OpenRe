"""Run lifecycle entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum


class RunStatus(str, Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TaskRunStatus(str, Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    RESUMED = "RESUMED"
    EVALUATING = "EVALUATING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"
    TIMED_OUT = "TIMED_OUT"


@dataclass(slots=True)
class RunSession:
    run_id: str
    dataset_id: str
    config_ids: list[str]
    status: RunStatus = RunStatus.CREATED
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    aggregate_metrics: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class TaskRun:
    task_run_id: str
    run_id: str
    task_id: str
    config_id: str
    status: TaskRunStatus = TaskRunStatus.CREATED
    final_output: str | None = None
    trace_id: str | None = None
    metrics: dict[str, float] = field(default_factory=dict)
    scores: dict[str, float] = field(default_factory=dict)
    failure_reason: str | None = None
