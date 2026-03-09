"""Trace domain entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum


class TraceEventKind(str, Enum):
    PROMPT_SENT = "prompt_sent"
    MODEL_OUTPUT = "model_output"
    TOOL_CALLED = "tool_called"
    TOOL_RESULT = "tool_result"
    HANDOFF = "handoff"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_RECEIVED = "approval_received"
    ERROR = "error"
    COMPLETED = "completed"


@dataclass(slots=True)
class TraceEvent:
    event_id: str
    run_id: str
    task_run_id: str
    kind: TraceEventKind
    payload: dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
