"""Runtime settings for the workbench."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(slots=True)
class Settings:
    """Environment-backed settings."""

    environment: str = "dev"
    default_dataset: str = "datasets/research_assistant_v1"
    trace_sink: str = "local_json"
    sqlite_path: str = ".artifacts/awb.db"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            environment=os.getenv("AWB_ENV", "dev"),
            default_dataset=os.getenv("AWB_DEFAULT_DATASET", "datasets/research_assistant_v1"),
            trace_sink=os.getenv("AWB_TRACE_SINK", "local_json"),
            sqlite_path=os.getenv("AWB_SQLITE_PATH", ".artifacts/awb.db"),
        )
