from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def test_seeded_dataset_meets_issue_contract() -> None:
    dataset_root = Path("datasets/research_assistant_v1")

    dataset_card = (dataset_root / "dataset_card.md").read_text(encoding="utf-8")
    assert "## Safety notes" in dataset_card
    assert "## Composition" in dataset_card

    tasks = _read_jsonl(dataset_root / "tasks.jsonl")
    assert len(tasks) >= 5

    rubric = (dataset_root / "grading_rubric.yaml").read_text(encoding="utf-8")
    assert "output_quality:" in rubric
    assert "trace_quality:" in rubric


def test_seed_script_is_idempotent_and_writes_expected_layout(tmp_path: Path) -> None:
    repo_root = Path.cwd()
    script = repo_root / "scripts" / "seed_dataset.py"

    for _ in range(2):
        subprocess.run(
            [sys.executable, str(script), "--root", str(tmp_path)],
            check=True,
            capture_output=True,
            text=True,
        )

    dataset_root = tmp_path / "datasets" / "research_assistant_v1"
    assert dataset_root.exists()

    for relative in [
        "dataset_card.md",
        "tasks.jsonl",
        "expected_outputs.jsonl",
        "grading_rubric.yaml",
        "splits/train.jsonl",
        "splits/dev.jsonl",
        "splits/test.jsonl",
    ]:
        assert (dataset_root / relative).exists()

    tasks = _read_jsonl(dataset_root / "tasks.jsonl")
    expected_outputs = _read_jsonl(dataset_root / "expected_outputs.jsonl")
    train = _read_jsonl(dataset_root / "splits/train.jsonl")
    dev = _read_jsonl(dataset_root / "splits/dev.jsonl")
    test = _read_jsonl(dataset_root / "splits/test.jsonl")

    task_ids = {str(row["task_id"]) for row in tasks}
    expected_ids = {str(row["task_id"]) for row in expected_outputs}
    split_ids = {str(row["task_id"]) for row in [*train, *dev, *test]}

    assert expected_ids == task_ids
    assert split_ids == task_ids
