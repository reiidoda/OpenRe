"""Approval service."""

from __future__ import annotations

from dataclasses import dataclass

from agent_workbench.domain.entities.approval import ApprovalRequest, ApprovalStatus
from agent_workbench.domain.interfaces.approval_gateway import ApprovalGateway


@dataclass(slots=True)
class ApprovalService:
    gateway: ApprovalGateway

    def request(self, approval: ApprovalRequest) -> None:
        self.gateway.submit(approval)

    def decide(self, request_id: str, status: ApprovalStatus, approver: str) -> None:
        self.gateway.resolve(request_id=request_id, status=status, approver=approver)
