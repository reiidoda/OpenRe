"""Simple risk classifier."""

from __future__ import annotations

from agent_workbench.domain.value_objects.risk_level import RiskLevel


def classify_action(action: str) -> RiskLevel:
    lowered = action.lower()
    if any(token in lowered for token in ["delete", "purchase", "transfer"]):
        return RiskLevel.CRITICAL
    if any(token in lowered for token in ["login", "submit", "edit", "write"]):
        return RiskLevel.HIGH
    if any(token in lowered for token in ["navigate", "open browser", "crawl"]):
        return RiskLevel.MEDIUM
    return RiskLevel.LOW
