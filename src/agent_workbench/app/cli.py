"""CLI entrypoint for Open Agent Workbench."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any
from typing import Mapping
from typing import Sequence
from typing import TextIO

import yaml

from agent_workbench.optimizer.best_config_registry import BestConfigRegistry
from agent_workbench.optimizer.config_search import WeightedObjectiveRanker
from agent_workbench.optimizer.dev_test_loop import DevTestOptimizationLoop
from agent_workbench.orchestration.runner import Runner


def _emit(payload: dict[str, Any], *, stream: TextIO | None = None) -> None:
    if stream is None:
        stream = sys.stdout
    stream.write(json.dumps(payload, indent=2, sort_keys=True))
    stream.write("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="openre", description="OpenRe CLI")
    parser.add_argument(
        "--artifact-root",
        default=".artifacts",
        help="Directory for generated traces and report artifacts.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run benchmark for one agent config")
    run.add_argument("--dataset", required=True)
    run.add_argument("--config", required=True)

    compare = sub.add_parser("compare", help="Run benchmark for multiple configs")
    compare.add_argument("--dataset", required=True)
    compare.add_argument("--configs", nargs="+", required=True)

    evaluate = sub.add_parser("eval", help="Evaluate a previous run")
    evaluate.add_argument("--run-id", required=True)

    optimize = sub.add_parser("optimize", help="Run optimizer search")
    optimize.add_argument("--dataset", required=True)
    optimize.add_argument("--search-space", required=True)

    best_config = sub.add_parser("best-config", help="Get current best config for a dataset")
    best_config.add_argument("--dataset", required=True)

    approve = sub.add_parser("approve", help="Resolve approval request")
    approve.add_argument("--request-id", required=True)
    approve.add_argument("--decision", choices=["approve", "deny"], required=True)

    report = sub.add_parser("report", help="Get report paths")
    report.add_argument("--run-id", required=True)
    report.add_argument("--format", choices=["json", "csv", "html"], required=True)

    return parser


def _planned(command: str, **fields: Any) -> dict[str, Any]:
    return {"command": command, "status": "planned", **fields}


def _coerce_float(value: object) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return 0.0
    return 0.0


def _as_mapping(value: object, field_name: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be a mapping.")
    result: dict[str, object] = {}
    for key, item in value.items():
        if isinstance(key, str):
            result[key] = item
    return result


def _load_search_space(path: Path) -> dict[str, object]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    return _as_mapping(loaded, str(path))


def _dataset_id(dataset_arg: str) -> str:
    return Path(dataset_arg).name


def _load_candidates(search_space: dict[str, object]) -> list[dict[str, object]]:
    raw_candidates = search_space.get("candidates")
    if not isinstance(raw_candidates, list):
        raise ValueError("search-space file must include a 'candidates' list.")
    candidates: list[dict[str, object]] = []
    for index, raw in enumerate(raw_candidates):
        if not isinstance(raw, dict):
            raise ValueError(f"candidates[{index}] must be a mapping.")
        candidates.append(dict(raw))
    if not candidates:
        raise ValueError("search-space file must include at least one candidate.")
    return candidates


def _metrics_for_split(
    *,
    candidate: dict[str, object],
    split: str,
    objective_metrics: list[str],
) -> dict[str, float]:
    split_key = f"{split}_metrics"
    split_metrics_raw = candidate.get(split_key)
    split_metrics = split_metrics_raw if isinstance(split_metrics_raw, dict) else {}
    source: Mapping[str, object] = split_metrics if split_metrics else candidate
    metrics: dict[str, float] = {}
    for metric in objective_metrics:
        metrics[metric] = _coerce_float(source.get(metric))
    return metrics


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    runner = Runner(artifact_root=Path(args.artifact_root))

    try:
        if args.command == "run":
            payload = {
                "command": "run",
                **runner.run(dataset=args.dataset, config_paths=[args.config]),
            }
            _emit(payload)
            return 0

        if args.command == "compare":
            if len(args.configs) < 2:
                raise ValueError("compare requires at least 2 config paths via --configs.")
            payload = {
                "command": "compare",
                **runner.run(dataset=args.dataset, config_paths=args.configs),
            }
            _emit(payload)
            return 0

        if args.command == "eval":
            _emit(
                _planned(
                    "eval",
                    run_id=args.run_id,
                    message="Eval pipeline scaffolded",
                )
            )
            return 0

        if args.command == "optimize":
            search_space_path = Path(args.search_space)
            search_space = _load_search_space(search_space_path)
            candidates = _load_candidates(search_space)
            dataset_id = _dataset_id(args.dataset)

            ranker_config_raw = search_space.get("ranker")
            ranker_config = ranker_config_raw if isinstance(ranker_config_raw, dict) else {}
            ranker = WeightedObjectiveRanker.from_config(ranker_config)
            objective_metrics = sorted(ranker.resolved_weights().keys())

            promotion_raw = search_space.get("promotion")
            promotion = promotion_raw if isinstance(promotion_raw, dict) else {}
            loop = DevTestOptimizationLoop(
                ranker=ranker,
                min_test_score=_coerce_float(promotion.get("min_test_score", 0.0)),
                max_dev_test_drop=_coerce_float(promotion.get("max_dev_test_drop", 0.10)),
            )
            result = loop.run(
                dataset_path=args.dataset,
                candidates=candidates,
                evaluate_candidate=lambda candidate, _tasks, split: _metrics_for_split(
                    candidate=candidate,
                    split=split,
                    objective_metrics=objective_metrics,
                ),
            )
            best_record: dict[str, object] | None = None
            if result.promoted and result.selected_candidate_id:
                selected_candidate = next(
                    (
                        candidate
                        for candidate in candidates
                        if str(candidate.get("candidate_id")) == result.selected_candidate_id
                    ),
                    None,
                )
                if selected_candidate is not None:
                    selected_metrics = _metrics_for_split(
                        candidate=selected_candidate,
                        split="test",
                        objective_metrics=objective_metrics,
                    )
                    scored_candidate = {
                        "candidate_id": result.selected_candidate_id,
                        **selected_metrics,
                    }
                    registry = BestConfigRegistry(
                        store_path=Path(args.artifact_root) / "state" / "best_configs.json"
                    )
                    best_record = registry.set(
                        dataset_id,
                        result.selected_candidate_id,
                        score_breakdown=ranker.score_breakdown(scored_candidate),
                        objective_score=ranker.score(scored_candidate),
                        metadata={
                            "source": "optimize",
                            "search_space": args.search_space,
                            "dev_run_id": result.dev.run_id,
                            "test_run_id": result.test.run_id,
                        },
                    )
            _emit(
                {
                    "command": "optimize",
                    "dataset": dataset_id,
                    "search_space": args.search_space,
                    "selected_candidate_id": result.selected_candidate_id,
                    "promoted": result.promoted,
                    "promotion_reason": result.promotion_reason,
                    "registry_updated": bool(best_record),
                    "best_config": best_record,
                    "dev_run": {
                        "run_id": result.dev.run_id,
                        "task_ids": result.dev.task_ids,
                        "ranking": result.dev.ranking,
                        "candidate_scores": result.dev.candidate_scores,
                        "selected_candidate_id": result.dev.selected_candidate_id,
                    },
                    "test_run": {
                        "run_id": result.test.run_id,
                        "task_ids": result.test.task_ids,
                        "ranking": result.test.ranking,
                        "candidate_scores": result.test.candidate_scores,
                        "selected_candidate_id": result.test.selected_candidate_id,
                    },
                }
            )
            return 0

        if args.command == "best-config":
            dataset_id = _dataset_id(args.dataset)
            registry = BestConfigRegistry(
                store_path=Path(args.artifact_root) / "state" / "best_configs.json"
            )
            record = registry.get(dataset_id)
            if record is None:
                _emit(
                    {
                        "command": "best-config",
                        "dataset": dataset_id,
                        "status": "not_found",
                    }
                )
                return 0
            _emit(
                {
                    "command": "best-config",
                    "dataset": dataset_id,
                    "status": "ok",
                    "best_config": record,
                }
            )
            return 0

        if args.command == "approve":
            _emit(
                {
                    "command": "approve",
                    "request_id": args.request_id,
                    "decision": args.decision,
                    "status": "recorded",
                }
            )
            return 0

        if args.command == "report":
            run_dir = Path(args.artifact_root) / "reports" / args.run_id / "v1"
            _emit(
                {
                    "command": "report",
                    "run_id": args.run_id,
                    "format": args.format,
                    "path": str(run_dir / f"report.{args.format}"),
                }
            )
            return 0

    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        _emit(
            {
                "command": str(args.command),
                "status": "error",
                "error": {"type": exc.__class__.__name__, "message": str(exc)},
            },
            stream=sys.stderr,
        )
        return 1

    _emit(
        {"status": "error", "error": {"type": "UnknownCommand", "message": "Unsupported command"}}
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
