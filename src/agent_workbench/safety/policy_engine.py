"""Policy evaluation chain."""

from __future__ import annotations

from dataclasses import dataclass

from agent_workbench.domain.value_objects.risk_level import RiskLevel


@dataclass(slots=True)
class PolicyDecision:
    allowed: bool
    requires_approval: bool
    reason: str


@dataclass(slots=True)
class PolicyEngine:
    require_approval_for: list[RiskLevel]
    deny_levels: list[RiskLevel]

    def evaluate(self, risk: RiskLevel) -> PolicyDecision:
        if risk in self.deny_levels:
            return PolicyDecision(allowed=False, requires_approval=False, reason="Denied by policy")
        if risk in self.require_approval_for:
            return PolicyDecision(allowed=True, requires_approval=True, reason="Approval required")
        return PolicyDecision(allowed=True, requires_approval=False, reason="Allowed")
