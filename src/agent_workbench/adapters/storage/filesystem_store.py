"""Filesystem artifact store."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class FilesystemStore:
    root: Path

    def __post_init__(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)

    def resolve_path(self, relative_path: str) -> Path:
        target = self.root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def run_trace_path(self, run_id: str, filename: str = "trace.jsonl") -> Path:
        return self.resolve_path(f"traces/{run_id}/{filename}")

    def run_report_path(self, run_id: str, relative_report_path: str) -> Path:
        return self.resolve_path(f"reports/{run_id}/{relative_report_path}")

    def put_text(self, relative_path: str, payload: str) -> str:
        target = self.resolve_path(relative_path)
        target.write_text(payload, encoding="utf-8")
        return str(target.resolve())

    def get_text(self, relative_path: str) -> str:
        return (self.root / relative_path).read_text(encoding="utf-8")

    def put_run_trace(self, run_id: str, payload: str, filename: str = "trace.jsonl") -> str:
        target = self.run_trace_path(run_id, filename)
        target.write_text(payload, encoding="utf-8")
        return str(target.resolve())

    def get_run_trace(self, run_id: str, filename: str = "trace.jsonl") -> str:
        return self.run_trace_path(run_id, filename).read_text(encoding="utf-8")

    def put_run_report(self, run_id: str, relative_report_path: str, payload: str) -> str:
        target = self.run_report_path(run_id, relative_report_path)
        target.write_text(payload, encoding="utf-8")
        return str(target.resolve())

    def get_run_report(self, run_id: str, relative_report_path: str) -> str:
        return self.run_report_path(run_id, relative_report_path).read_text(encoding="utf-8")
