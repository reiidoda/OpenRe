"""Dataset loader for local JSONL benchmark tasks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent_workbench.adapters.local.loader_errors import LoaderValidationError
from agent_workbench.domain.entities.task import TaskModality, TaskSpec
from agent_workbench.domain.value_objects.risk_level import RiskLevel


class JsonlDatasetProvider:
    """Loads and validates `tasks.jsonl` files into typed `TaskSpec` objects."""

    def load_tasks(self, dataset_path: str) -> list[TaskSpec]:
        dataset_root = Path(dataset_path)
        tasks_path = dataset_root / "tasks.jsonl"

        if not tasks_path.exists():
            raise LoaderValidationError(
                f"Dataset validation failed: missing required file '{tasks_path}'."
            )

        tasks: list[TaskSpec] = []
        for line_no, raw_line in enumerate(tasks_path.read_text(encoding="utf-8").splitlines(), start=1):
            if not raw_line.strip():
                continue
            try:
                payload = json.loads(raw_line)
            except json.JSONDecodeError as exc:
                raise LoaderValidationError(
                    f"Dataset validation failed: invalid JSON at '{tasks_path}:{line_no}' ({exc.msg})."
                ) from exc

            tasks.append(self._parse_task(payload=payload, source=tasks_path, line_no=line_no))

        if not tasks:
            raise LoaderValidationError(
                f"Dataset validation failed: '{tasks_path}' contains no task rows."
            )

        return tasks

    def _parse_task(self, payload: dict[str, Any], source: Path, line_no: int) -> TaskSpec:
        task_id = self._require_str(payload, "task_id", source, line_no)
        instruction = self._require_str(payload, "instruction", source, line_no)
        modality_raw = self._require_str(payload, "modality", source, line_no)
        risk_raw = self._require_str(payload, "risk_label", source, line_no)

        modality = self._parse_modality(modality_raw=modality_raw, source=source, line_no=line_no)
        risk_level = self._parse_risk(risk_raw=risk_raw, source=source, line_no=line_no)

        tags_value = payload.get("tags", [])
        if not isinstance(tags_value, list) or any(not isinstance(tag, str) for tag in tags_value):
            raise LoaderValidationError(
                f"Dataset validation failed: field 'tags' must be a list[str] at '{source}:{line_no}'."
            )

        return TaskSpec(
            task_id=task_id,
            instruction=instruction,
            modality=modality,
            risk_profile=risk_level,
            tags=tags_value,
        )

    @staticmethod
    def _require_str(payload: dict[str, Any], field: str, source: Path, line_no: int) -> str:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            raise LoaderValidationError(
                f"Dataset validation failed: field '{field}' must be a non-empty string at '{source}:{line_no}'."
            )
        return value.strip()

    @staticmethod
    def _parse_modality(modality_raw: str, source: Path, line_no: int) -> TaskModality:
        try:
            return TaskModality(modality_raw.lower())
        except ValueError as exc:
            allowed = ", ".join(mod.value for mod in TaskModality)
            raise LoaderValidationError(
                "Dataset validation failed: "
                f"invalid modality '{modality_raw}' at '{source}:{line_no}'. "
                f"Allowed values: {allowed}."
            ) from exc

    @staticmethod
    def _parse_risk(risk_raw: str, source: Path, line_no: int) -> RiskLevel:
        normalized = risk_raw.upper()
        if normalized not in RiskLevel.__members__:
            allowed = ", ".join(member for member in RiskLevel.__members__)
            raise LoaderValidationError(
                "Dataset validation failed: "
                f"invalid risk_label '{risk_raw}' at '{source}:{line_no}'. "
                f"Allowed values: {allowed}."
            )
        return RiskLevel[normalized]
