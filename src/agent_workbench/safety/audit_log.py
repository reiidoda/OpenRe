"""Audit log writer."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agent_workbench.utils.clock import utc_now_iso


@dataclass(slots=True)
class AuditLog:
    path: Path

    def write(self, event: str) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as file:
            file.write(f"{utc_now_iso()}\t{event}\n")
