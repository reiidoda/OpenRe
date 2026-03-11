"""SQLite storage helper."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sqlite3
from typing import Any


@dataclass(slots=True)
class SqliteStore:
    db_path: Path

    def connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute("CREATE TABLE IF NOT EXISTS key_value (k TEXT PRIMARY KEY, v TEXT NOT NULL)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
              run_id TEXT PRIMARY KEY,
              dataset_id TEXT NOT NULL,
              status TEXT NOT NULL,
              task_runs INTEGER NOT NULL,
              trace_path TEXT NOT NULL,
              config_ids_json TEXT NOT NULL,
              artifacts_json TEXT NOT NULL
            )
            """
        )
        conn.commit()
        return conn

    def put(self, key: str, value: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO key_value(k, v) VALUES(?, ?) ON CONFLICT(k) DO UPDATE SET v=excluded.v",
                (key, value),
            )
            conn.commit()

    def get(self, key: str) -> str | None:
        with self.connect() as conn:
            row = conn.execute("SELECT v FROM key_value WHERE k = ?", (key,)).fetchone()
            return row[0] if row else None

    def put_run_metadata(
        self,
        *,
        run_id: str,
        dataset_id: str,
        status: str,
        task_runs: int,
        trace_path: str,
        config_ids: list[str],
        artifacts: list[str],
    ) -> None:
        payload = (
            run_id,
            dataset_id,
            status,
            task_runs,
            trace_path,
            json.dumps(config_ids),
            json.dumps(artifacts),
        )
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO runs (
                  run_id, dataset_id, status, task_runs, trace_path, config_ids_json, artifacts_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                  dataset_id=excluded.dataset_id,
                  status=excluded.status,
                  task_runs=excluded.task_runs,
                  trace_path=excluded.trace_path,
                  config_ids_json=excluded.config_ids_json,
                  artifacts_json=excluded.artifacts_json
                """,
                payload,
            )
            conn.commit()

    def get_run_metadata(self, run_id: str) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT run_id, dataset_id, status, task_runs, trace_path, config_ids_json, artifacts_json
                FROM runs
                WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()
        if row is None:
            return None
        config_ids_raw = json.loads(str(row[5]))
        artifacts_raw = json.loads(str(row[6]))
        config_ids = (
            [str(item) for item in config_ids_raw] if isinstance(config_ids_raw, list) else []
        )
        artifacts = [str(item) for item in artifacts_raw] if isinstance(artifacts_raw, list) else []
        return {
            "run_id": str(row[0]),
            "dataset_id": str(row[1]),
            "status": str(row[2]),
            "task_runs": int(row[3]),
            "trace_path": str(row[4]),
            "config_ids": config_ids,
            "artifacts": artifacts,
        }
