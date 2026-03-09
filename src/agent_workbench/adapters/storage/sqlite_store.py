"""SQLite storage helper."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3


@dataclass(slots=True)
class SqliteStore:
    db_path: Path

    def connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS key_value (k TEXT PRIMARY KEY, v TEXT NOT NULL)"
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
