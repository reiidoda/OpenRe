"""Tool domain entities."""

from __future__ import annotations

from dataclasses import dataclass, field

from agent_workbench.domain.value_objects.risk_level import RiskLevel


@dataclass(slots=True)
class ToolSpec:
    tool_id: str
    description: str
    risk_level: RiskLevel
    schema: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class ToolCommand:
    tool_id: str
    arguments: dict[str, object]


@dataclass(slots=True)
class ToolResult:
    success: bool
    output: str
    metadata: dict[str, str] = field(default_factory=dict)
