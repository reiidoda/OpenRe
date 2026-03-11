"""Dev/test split optimization loop orchestration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
import json
from pathlib import Path

from agent_workbench.adapters.local.dataset_loader import JsonlDatasetProvider
from agent_workbench.domain.entities.task import TaskSpec
from agent_workbench.optimizer.config_search import CandidateRanking
from agent_workbench.optimizer.config_search import WeightedObjectiveRanker
from agent_workbench.utils.ids import make_id

CandidateEvaluator = Callable[[dict[str, object], list[TaskSpec], str], dict[str, float]]


@dataclass(slots=True)
class SplitRunResult:
    split: str
    run_id: str
    task_ids: list[str]
    candidate_scores: dict[str, float]
    ranking: list[str]
    selected_candidate_id: str | None = None


@dataclass(slots=True)
class DevTestOptimizationResult:
    dataset_id: str
    selected_candidate_id: str | None
    promoted: bool
    promotion_reason: str
    dev: SplitRunResult
    test: SplitRunResult


def _candidate_id(candidate: dict[str, object]) -> str:
    for key in ("candidate_id", "id", "config_id", "name"):
        value = candidate.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return json.dumps(candidate, sort_keys=True, default=str)


def _load_split_ids(dataset_root: Path, split: str) -> list[str]:
    split_path = dataset_root / "splits" / f"{split}.jsonl"
    if not split_path.exists():
        raise ValueError(f"Missing split file: {split_path}")

    ids: list[str] = []
    for line_no, raw_line in enumerate(
        split_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON at {split_path}:{line_no}: {exc.msg}") from exc
        task_id = payload.get("task_id")
        if not isinstance(task_id, str) or not task_id.strip():
            raise ValueError(f"Missing task_id at {split_path}:{line_no}")
        ids.append(task_id.strip())

    if not ids:
        raise ValueError(f"Split {split} has no task ids in {split_path}")
    return ids


def _select_tasks(tasks: list[TaskSpec], task_ids: list[str], split: str) -> list[TaskSpec]:
    by_id = {task.task_id: task for task in tasks}
    missing = [task_id for task_id in task_ids if task_id not in by_id]
    if missing:
        raise ValueError(
            f"Split {split} references unknown task ids: {', '.join(sorted(set(missing)))}"
        )
    return [by_id[task_id] for task_id in task_ids]


@dataclass(slots=True)
class DevTestOptimizationLoop:
    dataset_provider: JsonlDatasetProvider = field(default_factory=JsonlDatasetProvider)
    ranker: WeightedObjectiveRanker = field(default_factory=WeightedObjectiveRanker)
    min_test_score: float = 0.0
    max_dev_test_drop: float = 0.10

    def run(
        self,
        *,
        dataset_path: str,
        candidates: list[dict[str, object]],
        evaluate_candidate: CandidateEvaluator,
    ) -> DevTestOptimizationResult:
        if not candidates:
            raise ValueError("At least one candidate is required.")

        dataset_root = Path(dataset_path)
        all_tasks = self.dataset_provider.load_tasks(str(dataset_root))
        dataset_id = dataset_root.name

        dev_ids = _load_split_ids(dataset_root, "dev")
        test_ids = _load_split_ids(dataset_root, "test")
        dev_tasks = _select_tasks(all_tasks, dev_ids, "dev")
        test_tasks = _select_tasks(all_tasks, test_ids, "test")

        dev_rankings = self._rank_split(
            split="dev",
            tasks=dev_tasks,
            candidates=candidates,
            evaluate_candidate=evaluate_candidate,
        )
        selected = dev_rankings[0].candidate if dev_rankings else None
        selected_id = dev_rankings[0].candidate_id if dev_rankings else None
        dev_scores = {item.candidate_id: item.score for item in dev_rankings}

        dev_result = SplitRunResult(
            split="dev",
            run_id=make_id("optdev"),
            task_ids=[task.task_id for task in dev_tasks],
            candidate_scores=dev_scores,
            ranking=[item.candidate_id for item in dev_rankings],
            selected_candidate_id=selected_id,
        )

        test_result = self._validate_on_test(
            selected_candidate=selected,
            selected_candidate_id=selected_id,
            tasks=test_tasks,
            evaluate_candidate=evaluate_candidate,
        )

        promoted, reason = self._promotion_decision(
            selected_candidate_id=selected_id,
            dev_score=dev_scores.get(selected_id) if selected_id else None,
            test_score=test_result.candidate_scores.get(selected_id) if selected_id else None,
        )
        return DevTestOptimizationResult(
            dataset_id=dataset_id,
            selected_candidate_id=selected_id,
            promoted=promoted,
            promotion_reason=reason,
            dev=dev_result,
            test=test_result,
        )

    def _rank_split(
        self,
        *,
        split: str,
        tasks: list[TaskSpec],
        candidates: list[dict[str, object]],
        evaluate_candidate: CandidateEvaluator,
    ) -> list[CandidateRanking]:
        scored: list[dict[str, object]] = []
        for candidate in candidates:
            metrics = evaluate_candidate(candidate, tasks, split)
            record = dict(candidate)
            record.update(metrics)
            record.setdefault("candidate_id", _candidate_id(candidate))
            scored.append(record)
        return self.ranker.rank_with_scores(scored)

    def _validate_on_test(
        self,
        *,
        selected_candidate: dict[str, object] | None,
        selected_candidate_id: str | None,
        tasks: list[TaskSpec],
        evaluate_candidate: CandidateEvaluator,
    ) -> SplitRunResult:
        if selected_candidate is None or selected_candidate_id is None:
            return SplitRunResult(
                split="test",
                run_id=make_id("opttest"),
                task_ids=[task.task_id for task in tasks],
                candidate_scores={},
                ranking=[],
                selected_candidate_id=None,
            )

        metrics = evaluate_candidate(selected_candidate, tasks, "test")
        evaluated = dict(selected_candidate)
        evaluated.update(metrics)
        evaluated["candidate_id"] = selected_candidate_id
        score = self.ranker.score(evaluated)
        return SplitRunResult(
            split="test",
            run_id=make_id("opttest"),
            task_ids=[task.task_id for task in tasks],
            candidate_scores={selected_candidate_id: score},
            ranking=[selected_candidate_id],
            selected_candidate_id=selected_candidate_id,
        )

    def _promotion_decision(
        self,
        *,
        selected_candidate_id: str | None,
        dev_score: float | None,
        test_score: float | None,
    ) -> tuple[bool, str]:
        if selected_candidate_id is None or dev_score is None or test_score is None:
            return False, "No candidate selected from dev split."
        if test_score < self.min_test_score:
            return (
                False,
                f"Test score {test_score:.4f} below promotion threshold {self.min_test_score:.4f}.",
            )
        drop = dev_score - test_score
        if drop > self.max_dev_test_drop:
            return (
                False,
                f"Dev-to-test drop {drop:.4f} exceeds allowed {self.max_dev_test_drop:.4f}.",
            )
        return True, "Candidate promoted."
