"""In-memory approval queue."""

from __future__ import annotations

from dataclasses import dataclass, field

from agent_workbench.domain.entities.approval import ApprovalRequest, ApprovalStatus


@dataclass(slots=True)
class ApprovalQueue:
    pending: dict[str, ApprovalRequest] = field(default_factory=dict)

    def submit(self, request: ApprovalRequest) -> None:
        self.pending[request.request_id] = request

    def resolve(self, request_id: str, status: ApprovalStatus, approver: str) -> None:
        request = self.pending[request_id]
        request.status = status
        request.approver = approver
