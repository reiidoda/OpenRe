"""Best configuration registry with atomic persistence."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from dataclasses import field
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from agent_workbench.utils.clock import utc_now_iso


def _coerce_float(value: object) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0


def _normalize_score_breakdown(raw: Mapping[str, object] | None) -> dict[str, float]:
    if raw is None:
        return {}
    return {str(metric): round(_coerce_float(score), 6) for metric, score in raw.items()}


@dataclass(slots=True)
class BestConfigRegistry:
    store_path: Path = Path(".artifacts/state/best_configs.json")
    entries: dict[str, dict[str, object]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.entries = self._load()

    def _load(self) -> dict[str, dict[str, object]]:
        if not self.store_path.exists():
            return {}
        loaded = json.loads(self.store_path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            return {}
        entries: dict[str, dict[str, object]] = {}
        for dataset_id, payload in loaded.items():
            if isinstance(dataset_id, str) and isinstance(payload, dict):
                entries[dataset_id] = dict(payload)
        return entries

    def _persist_atomic(self) -> None:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=str(self.store_path.parent),
            delete=False,
            suffix=".tmp",
        ) as handle:
            json.dump(self.entries, handle, indent=2, sort_keys=True)
            handle.write("\n")
            temp_path = Path(handle.name)
        os.replace(temp_path, self.store_path)

    def set(
        self,
        dataset_id: str,
        config_id: str,
        *,
        score_breakdown: Mapping[str, object] | None = None,
        objective_score: object = 0.0,
        timestamp: str | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> dict[str, object]:
        if not dataset_id.strip():
            raise ValueError("dataset_id must be non-empty.")
        if not config_id.strip():
            raise ValueError("config_id must be non-empty.")

        record: dict[str, object] = {
            "config_id": config_id.strip(),
            "score_breakdown": _normalize_score_breakdown(score_breakdown),
            "objective_score": round(_coerce_float(objective_score), 6),
            "updated_at": timestamp or utc_now_iso(),
        }
        if metadata:
            record["metadata"] = dict(metadata)

        self.entries[dataset_id.strip()] = record
        self._persist_atomic()
        return record

    def get(self, dataset_id: str) -> dict[str, object] | None:
        record = self.entries.get(dataset_id.strip())
        if record is None:
            return None
        return dict(record)
