"""Tool executor interface."""

from __future__ import annotations

from typing import Protocol

from agent_workbench.domain.entities.tool import ToolCommand, ToolResult


class ToolExecutor(Protocol):
    def execute(self, command: ToolCommand) -> ToolResult:
        """Execute a tool command."""
