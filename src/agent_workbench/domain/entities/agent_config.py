"""Agent configuration entities."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class AgentBudget:
    max_steps: int
    max_cost_usd: float


@dataclass(frozen=True, slots=True)
class AgentConfig:
    config_id: str
    provider: str
    model_config: str
    system_prompt: str
    tools: list[str] = field(default_factory=list)
    safety_policy_id: str = ""
    budgets: AgentBudget | None = None
