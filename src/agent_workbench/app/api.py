"""Minimal internal API facade."""

from __future__ import annotations

from dataclasses import dataclass

from agent_workbench.orchestration.runner import Runner


@dataclass(slots=True)
class Api:
    runner: Runner

    def create_run(self, dataset: str, config_paths: list[str]) -> dict[str, object]:
        return self.runner.run(dataset=dataset, config_paths=config_paths)
