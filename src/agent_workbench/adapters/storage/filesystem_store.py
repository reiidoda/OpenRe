"""Filesystem artifact store."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class FilesystemStore:
    root: Path

    def __post_init__(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)

    def put_text(self, relative_path: str, payload: str) -> str:
        target = self.root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload, encoding="utf-8")
        return str(target.resolve())

    def get_text(self, relative_path: str) -> str:
        return (self.root / relative_path).read_text(encoding="utf-8")
