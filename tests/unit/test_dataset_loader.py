from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_workbench.adapters.local.dataset_loader import JsonlDatasetProvider
from agent_workbench.adapters.local.loader_errors import LoaderValidationError
from agent_workbench.domain.entities.task import TaskModality


def test_dataset_loader_returns_typed_tasks() -> None:
    provider = JsonlDatasetProvider()

    tasks = provider.load_tasks("datasets/research_assistant_v1")

    assert len(tasks) >= 5
    assert tasks[0].task_id == "ra_001"
    assert isinstance(tasks[0].modality, TaskModality)


def test_dataset_loader_rejects_missing_instruction(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset"
    dataset.mkdir(parents=True)

    bad_task = {
        "task_id": "t_001",
        "modality": "text",
        "risk_label": "LOW",
        "tags": [],
    }
    (dataset / "tasks.jsonl").write_text(json.dumps(bad_task) + "\n", encoding="utf-8")

    provider = JsonlDatasetProvider()
    with pytest.raises(LoaderValidationError, match="field 'instruction'"):
        provider.load_tasks(str(dataset))


def test_dataset_loader_rejects_invalid_modality(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset"
    dataset.mkdir(parents=True)

    bad_task = {
        "task_id": "t_001",
        "instruction": "Hello",
        "modality": "audio",
        "risk_label": "LOW",
        "tags": [],
    }
    (dataset / "tasks.jsonl").write_text(json.dumps(bad_task) + "\n", encoding="utf-8")

    provider = JsonlDatasetProvider()
    with pytest.raises(LoaderValidationError, match="invalid modality 'audio'"):
        provider.load_tasks(str(dataset))
