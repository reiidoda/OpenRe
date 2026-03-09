"""Approval gateway interface."""

from __future__ import annotations

from typing import Protocol

from agent_workbench.domain.entities.approval import ApprovalRequest, ApprovalStatus


class ApprovalGateway(Protocol):
    def submit(self, request: ApprovalRequest) -> None:
        """Submit approval request."""

    def resolve(self, request_id: str, status: ApprovalStatus, approver: str) -> None:
        """Resolve approval request."""
