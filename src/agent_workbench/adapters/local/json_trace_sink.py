"""Local JSONL trace sink."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent_workbench.domain.entities.trace import TraceEvent
from agent_workbench.utils.serialization import dumps


@dataclass(slots=True)
class JsonTraceSink:
    output_path: Path

    def __post_init__(self) -> None:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def _event_record(self, event: TraceEvent) -> dict[str, Any]:
        return {
            "event_id": event.event_id,
            "run_id": event.run_id,
            "task_run_id": event.task_run_id,
            "kind": event.kind.value,
            "timestamp": event.timestamp.isoformat(),
            "payload": event.payload,
        }

    def write(self, event: TraceEvent) -> None:
        with self.output_path.open("a", encoding="utf-8") as file:
            file.write(dumps(self._event_record(event)))
            file.write("\n")
