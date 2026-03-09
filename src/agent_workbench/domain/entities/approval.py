"""Approval request entity."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from agent_workbench.domain.value_objects.risk_level import RiskLevel


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"


@dataclass(slots=True)
class ApprovalRequest:
    request_id: str
    task_run_id: str
    action: str
    risk_level: RiskLevel
    policy_reason: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    approver: str | None = None
