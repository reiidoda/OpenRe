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
    sqlite_path: str = ".artifacts/openre.db"

    @classmethod
    def from_env(cls) -> "Settings":
        environment = os.getenv("OPENRE_ENV", os.getenv("AWB_ENV", "dev"))
        default_dataset = os.getenv(
            "OPENRE_DEFAULT_DATASET",
            os.getenv("AWB_DEFAULT_DATASET", "datasets/research_assistant_v1"),
        )
        trace_sink = os.getenv("OPENRE_TRACE_SINK", os.getenv("AWB_TRACE_SINK", "local_json"))
        sqlite_path = os.getenv(
            "OPENRE_SQLITE_PATH",
            os.getenv("AWB_SQLITE_PATH", ".artifacts/openre.db"),
        )
        return cls(
            environment=environment,
            default_dataset=default_dataset,
            trace_sink=trace_sink,
            sqlite_path=sqlite_path,
        )
