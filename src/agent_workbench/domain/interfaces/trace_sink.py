"""Trace sink interface."""

from __future__ import annotations

from typing import Protocol

from agent_workbench.domain.entities.trace import TraceEvent


class TraceSink(Protocol):
    def write(self, event: TraceEvent) -> None:
        """Persist a trace event."""
