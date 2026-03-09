"""Task domain entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from agent_workbench.domain.value_objects.risk_level import RiskLevel


class TaskModality(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    BROWSER = "browser"
    COMPUTER = "computer"


@dataclass(slots=True)
class TaskSpec:
    task_id: str
    instruction: str
    modality: TaskModality
    risk_profile: RiskLevel
    expected_artifacts: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
