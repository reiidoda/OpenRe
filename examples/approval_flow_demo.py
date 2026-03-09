from agent_workbench.domain.entities.approval import ApprovalRequest, ApprovalStatus
from agent_workbench.domain.value_objects.risk_level import RiskLevel
from agent_workbench.safety.approval_queue import ApprovalQueue


if __name__ == "__main__":
    queue = ApprovalQueue()
    request = ApprovalRequest(
        request_id="apr_demo",
        task_run_id="taskrun_demo",
        action="submit form",
        risk_level=RiskLevel.HIGH,
        policy_reason="High-risk browser action",
    )
    queue.submit(request)
    queue.resolve("apr_demo", ApprovalStatus.APPROVED, "human_1")
    print(queue.pending["apr_demo"])
