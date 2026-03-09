"""Run orchestration service."""

from __future__ import annotations

from dataclasses import dataclass

from agent_workbench.domain.entities.run import RunSession, RunStatus
from agent_workbench.utils.ids import make_id


@dataclass(slots=True)
class RunService:
    def create_session(self, dataset_id: str, config_ids: list[str]) -> RunSession:
        return RunSession(run_id=make_id("run"), dataset_id=dataset_id, config_ids=config_ids)

    def mark_running(self, session: RunSession) -> None:
        session.status = RunStatus.RUNNING

    def mark_completed(self, session: RunSession, metrics: dict[str, float]) -> None:
        session.status = RunStatus.COMPLETED
        session.aggregate_metrics = metrics
