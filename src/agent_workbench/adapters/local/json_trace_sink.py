"""Local JSONL trace sink."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agent_workbench.domain.entities.trace import TraceEvent
from agent_workbench.utils.serialization import dumps


@dataclass(slots=True)
class JsonTraceSink:
    output_path: Path

    def __post_init__(self) -> None:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, event: TraceEvent) -> None:
        with self.output_path.open("a", encoding="utf-8") as file:
            file.write(dumps(event))
            file.write("\n")
